#define _POSIX_C_SOURCE 200809L

#include <vulkan/vulkan.h>

#include <ctype.h>
#include <errno.h>
#include <inttypes.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "shader_spv.h"

#define MAX_ACCOUNTS 8
#define MAX_ACCOUNT_SIZE 0x1000u
#define MAX_HEX_WRITE 0x400u
#define HOST_ARENA_SIZE (1u << 24)
#define QUOTE_MEMO_BYTES 8u
#define MAX_MARKETS 8u
#define MAX_MARKET_OUTCOME_SLOTS 32768u
#define MIN_MARKET_OUTCOME_SLOTS 32768u
#define MAX_MARKET_MEMO_BYTES 256u
#define MIN_PRICE_INDEX 32768u
#define MAX_PRICE_INDEX 300000u
#define RESOLUTION_WORDS 64u

typedef struct {
    uint32_t mode;
    uint32_t index;
    uint32_t value;
} Push;

typedef struct {
    bool used;
    VkBuffer buf;
    VkDeviceMemory mem;
    uint8_t *map;
    VkDeviceSize size;
} AccountBuf;

typedef struct {
    VkBuffer buf;
    VkDeviceMemory mem;
    uint8_t *map;
    VkDeviceSize size;
} RawBuf;

typedef struct {
    uint32_t storage_count;
    uint32_t memo_bytes;
    VkDescriptorSetLayout layout;
    VkDescriptorSet set;
} MarketBook;

typedef struct {
    VkInstance instance;
    VkPhysicalDevice phys;
    VkDevice device;
    VkQueue queue;
    uint32_t qfam;
    VkPhysicalDeviceProperties props;
    VkPhysicalDeviceMemoryProperties mem_props;

    VkCommandPool cmd_pool;
    VkCommandBuffer cmd;

    VkDescriptorSetLayout quote_layout;
    VkDescriptorSetLayout settlement_layout;
    VkDescriptorPool desc_pool;
    VkDescriptorSet quote_book;
    VkDescriptorSet settlement_book;
    MarketBook markets[MAX_MARKETS];
    uint32_t market_count;
    uint32_t outcome_slot_total;
    uint32_t memo_byte_total;

    VkPipelineLayout pipe_layout;
    VkPipeline pipeline;

    AccountBuf accounts[MAX_ACCOUNTS];
    RawBuf oracle_buf;
    RawBuf clearing_buf;
    RawBuf public_quote_buf;

    bool armed;
    bool quoted;
    uint32_t resolution_words;
    char resolution[256];
} App;

static uint8_t host_arena[HOST_ARENA_SIZE];
static size_t host_arena_off;
static struct {
    void *ptr;
    size_t size;
} host_recs[8192];

static void die(const char *msg) {
    fprintf(stderr, "fatal: %s\n", msg);
    exit(1);
}

static void die_vk(const char *what, VkResult res) {
    fprintf(stderr, "fatal: %s: VkResult %d\n", what, res);
    exit(1);
}

#define VK_CHECK(expr) do { \
    VkResult _res = (expr); \
    if (_res != VK_SUCCESS) die_vk(#expr, _res); \
} while (0)

static size_t align_up_size(size_t v, size_t a) {
    if (a <= 1) {
        return v;
    }
    size_t r = v % a;
    return r ? v + (a - r) : v;
}

static VKAPI_ATTR void *VKAPI_CALL host_alloc(void *user,
                                              size_t size,
                                              size_t alignment,
                                              VkSystemAllocationScope scope) {
    (void)user;
    (void)scope;

    if (alignment < sizeof(void *)) {
        alignment = sizeof(void *);
    }

    size_t ptr_off = align_up_size(host_arena_off, alignment);
    if (ptr_off + size > sizeof(host_arena)) {
        return NULL;
    }

    void *ptr = host_arena + ptr_off;
    memset(ptr, 0, size);
    host_arena_off = ptr_off + size;
    for (size_t i = 0; i < sizeof(host_recs) / sizeof(host_recs[0]); i++) {
        if (!host_recs[i].ptr) {
            host_recs[i].ptr = ptr;
            host_recs[i].size = size;
            break;
        }
    }
    return ptr;
}

static VKAPI_ATTR void *VKAPI_CALL host_realloc(void *user,
                                                void *orig,
                                                size_t size,
                                                size_t alignment,
                                                VkSystemAllocationScope scope) {
    if (!orig) {
        return host_alloc(user, size, alignment, scope);
    }
    if (!size) {
        return NULL;
    }

    void *new_ptr = host_alloc(user, size, alignment, scope);
    if (new_ptr) {
        size_t old_size = 0;
        for (size_t i = 0; i < sizeof(host_recs) / sizeof(host_recs[0]); i++) {
            if (host_recs[i].ptr == orig) {
                old_size = host_recs[i].size;
                break;
            }
        }
        if (old_size) {
            memcpy(new_ptr, orig, old_size < size ? old_size : size);
        }
    }
    return new_ptr;
}

static VKAPI_ATTR void VKAPI_CALL host_free(void *user, void *ptr) {
    (void)user;
    (void)ptr;
}

static const VkAllocationCallbacks host_callbacks = {
    .pfnAllocation = host_alloc,
    .pfnReallocation = host_realloc,
    .pfnFree = host_free,
};

static bool read_line(char *buf, size_t len) {
    if (!fgets(buf, len, stdin)) {
        return false;
    }
    size_t n = strlen(buf);
    if (n && buf[n - 1] == '\n') {
        buf[n - 1] = 0;
    }
    return true;
}

static uint64_t ask_u64(const char *prompt) {
    char line[128];
    printf("%s", prompt);
    if (!read_line(line, sizeof(line))) {
        exit(0);
    }
    errno = 0;
    char *end = NULL;
    uint64_t v = strtoull(line, &end, 0);
    if (errno || end == line) {
        puts("bad number");
        return UINT64_MAX;
    }
    return v;
}

static int hex_value(int c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}

static int parse_hex(const char *s, uint8_t *out, size_t cap, size_t *out_len) {
    int hi = -1;
    size_t n = 0;
    for (; *s; s++) {
        if (isspace((unsigned char)*s)) {
            continue;
        }
        int v = hex_value((unsigned char)*s);
        if (v < 0) {
            return -1;
        }
        if (hi < 0) {
            hi = v;
        } else {
            if (n == cap) {
                return -1;
            }
            out[n++] = (uint8_t)((hi << 4) | v);
            hi = -1;
        }
    }
    if (hi >= 0) {
        return -1;
    }
    *out_len = n;
    return 0;
}

static uint32_t find_mem_type(App *app, uint32_t bits, VkMemoryPropertyFlags flags) {
    for (uint32_t i = 0; i < app->mem_props.memoryTypeCount; i++) {
        if ((bits & (1u << i)) &&
            (app->mem_props.memoryTypes[i].propertyFlags & flags) == flags) {
            return i;
        }
    }
    die("no matching memory type");
    return 0;
}

static bool device_has_ext(VkPhysicalDevice phys, const char *name) {
    uint32_t count = 0;
    VK_CHECK(vkEnumerateDeviceExtensionProperties(phys, NULL, &count, NULL));
    VkExtensionProperties *exts = calloc(count, sizeof(*exts));
    if (!exts) die("calloc");
    VK_CHECK(vkEnumerateDeviceExtensionProperties(phys, NULL, &count, exts));
    bool found = false;
    for (uint32_t i = 0; i < count; i++) {
        if (!strcmp(exts[i].extensionName, name)) {
            found = true;
            break;
        }
    }
    free(exts);
    return found;
}

static void choose_device(App *app) {
    uint32_t count = 0;
    VK_CHECK(vkEnumeratePhysicalDevices(app->instance, &count, NULL));
    if (!count) {
        die("no Vulkan devices");
    }

    VkPhysicalDevice *devs = calloc(count, sizeof(*devs));
    if (!devs) die("calloc");
    VK_CHECK(vkEnumeratePhysicalDevices(app->instance, &count, devs));

    int chosen = -1;
    uint32_t chosen_q = 0;
    bool chosen_lvp = false;
    for (uint32_t i = 0; i < count; i++) {
        VkPhysicalDeviceProperties props;
        vkGetPhysicalDeviceProperties(devs[i], &props);

        uint32_t q_count = 0;
        vkGetPhysicalDeviceQueueFamilyProperties(devs[i], &q_count, NULL);
        VkQueueFamilyProperties *qs = calloc(q_count, sizeof(*qs));
        if (!qs) die("calloc");
        vkGetPhysicalDeviceQueueFamilyProperties(devs[i], &q_count, qs);

        for (uint32_t q = 0; q < q_count; q++) {
            if (!(qs[q].queueFlags & VK_QUEUE_COMPUTE_BIT)) {
                continue;
            }
            bool is_lvp = strstr(props.deviceName, "llvmpipe") ||
                          strstr(props.deviceName, "lavapipe");
            if (chosen < 0 || (is_lvp && !chosen_lvp)) {
                chosen = (int)i;
                chosen_q = q;
                chosen_lvp = is_lvp;
            }
            break;
        }
        free(qs);
    }

    if (chosen < 0) {
        die("no compute queue");
    }
    app->phys = devs[chosen];
    app->qfam = chosen_q;
    vkGetPhysicalDeviceProperties(app->phys, &app->props);
    vkGetPhysicalDeviceMemoryProperties(app->phys, &app->mem_props);
    free(devs);
}

static void make_raw_buffer(App *app, RawBuf *b, VkDeviceSize size) {
    VkBufferCreateInfo bci = {
        .sType = VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO,
        .size = size,
        .usage = VK_BUFFER_USAGE_STORAGE_BUFFER_BIT,
        .sharingMode = VK_SHARING_MODE_EXCLUSIVE,
    };
    VK_CHECK(vkCreateBuffer(app->device, &bci, NULL, &b->buf));

    VkMemoryRequirements req;
    vkGetBufferMemoryRequirements(app->device, b->buf, &req);
    VkMemoryAllocateInfo mai = {
        .sType = VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO,
        .allocationSize = req.size,
        .memoryTypeIndex = find_mem_type(app, req.memoryTypeBits,
                                         VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT |
                                         VK_MEMORY_PROPERTY_HOST_COHERENT_BIT),
    };
    VK_CHECK(vkAllocateMemory(app->device, &mai, NULL, &b->mem));
    VK_CHECK(vkBindBufferMemory(app->device, b->buf, b->mem, 0));
    VK_CHECK(vkMapMemory(app->device, b->mem, 0, size, 0, (void **)&b->map));
    memset(b->map, 0, (size_t)size);
    b->size = size;
}

static VkDescriptorBufferInfo desc_info(VkBuffer buf, VkDeviceSize off,
                                        VkDeviceSize range) {
    VkDescriptorBufferInfo info = {
        .buffer = buf,
        .offset = off,
        .range = range,
    };
    return info;
}

static void update_storage_desc(App *app, VkDescriptorSet set, uint32_t binding,
                                uint32_t array_elem, VkBuffer buf,
                                VkDeviceSize off, VkDeviceSize range) {
    VkDescriptorBufferInfo info = desc_info(buf, off, range);
    VkWriteDescriptorSet write = {
        .sType = VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET,
        .dstSet = set,
        .dstBinding = binding,
        .dstArrayElement = array_elem,
        .descriptorCount = 1,
        .descriptorType = VK_DESCRIPTOR_TYPE_STORAGE_BUFFER,
        .pBufferInfo = &info,
    };
    vkUpdateDescriptorSets(app->device, 1, &write, 0, NULL);
}

static void init_vulkan(App *app) {
    memset(app, 0, sizeof(*app));

    VkApplicationInfo app_info = {
        .sType = VK_STRUCTURE_TYPE_APPLICATION_INFO,
        .pApplicationName = "forecast exchange",
        .apiVersion = VK_API_VERSION_1_1,
    };
    VkInstanceCreateInfo ici = {
        .sType = VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
        .pApplicationInfo = &app_info,
        .enabledLayerCount = 0,
    };
    VK_CHECK(vkCreateInstance(&ici, NULL, &app->instance));
    choose_device(app);

    if (!device_has_ext(app->phys, VK_EXT_INLINE_UNIFORM_BLOCK_EXTENSION_NAME)) {
        die("lavapipe image lacks inline uniform block support");
    }

    float prio = 1.0f;
    VkDeviceQueueCreateInfo qci = {
        .sType = VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO,
        .queueFamilyIndex = app->qfam,
        .queueCount = 1,
        .pQueuePriorities = &prio,
    };
    const char *exts[] = {
        VK_EXT_INLINE_UNIFORM_BLOCK_EXTENSION_NAME,
    };
    VkPhysicalDeviceInlineUniformBlockFeatures inline_features = {
        .sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_INLINE_UNIFORM_BLOCK_FEATURES,
        .inlineUniformBlock = VK_TRUE,
        .descriptorBindingInlineUniformBlockUpdateAfterBind = VK_TRUE,
    };
    VkPhysicalDeviceFeatures features = {0};
    features.robustBufferAccess = VK_FALSE;
    VkDeviceCreateInfo dci = {
        .sType = VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO,
        .pNext = &inline_features,
        .queueCreateInfoCount = 1,
        .pQueueCreateInfos = &qci,
        .enabledExtensionCount = 1,
        .ppEnabledExtensionNames = exts,
        .enabledLayerCount = 0,
        .pEnabledFeatures = &features,
    };
    VK_CHECK(vkCreateDevice(app->phys, &dci, &host_callbacks, &app->device));
    vkGetDeviceQueue(app->device, app->qfam, 0, &app->queue);

    VkCommandPoolCreateInfo cpci = {
        .sType = VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO,
        .flags = VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT,
        .queueFamilyIndex = app->qfam,
    };
    VK_CHECK(vkCreateCommandPool(app->device, &cpci, NULL, &app->cmd_pool));

    VkCommandBufferAllocateInfo cbai = {
        .sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO,
        .commandPool = app->cmd_pool,
        .level = VK_COMMAND_BUFFER_LEVEL_PRIMARY,
        .commandBufferCount = 1,
    };
    VK_CHECK(vkAllocateCommandBuffers(app->device, &cbai, &app->cmd));
}

static void create_market_layouts(App *app) {
    VkDescriptorSetLayoutBinding quote_bindings[2] = {
        {
            .binding = 0,
            .descriptorType = VK_DESCRIPTOR_TYPE_STORAGE_BUFFER,
            .descriptorCount = 1,
            .stageFlags = VK_SHADER_STAGE_COMPUTE_BIT,
        },
        {
            .binding = 1,
            .descriptorType = VK_DESCRIPTOR_TYPE_INLINE_UNIFORM_BLOCK,
            .descriptorCount = QUOTE_MEMO_BYTES,
            .stageFlags = VK_SHADER_STAGE_COMPUTE_BIT,
        },
    };
    VkDescriptorSetLayoutCreateInfo quote_ci = {
        .sType = VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_CREATE_INFO,
        .bindingCount = 2,
        .pBindings = quote_bindings,
    };
    VK_CHECK(vkCreateDescriptorSetLayout(app->device, &quote_ci, NULL,
                                         &app->quote_layout));

    VkDescriptorSetLayoutBinding settlement_bindings[2] = {
        {
            .binding = 0,
            .descriptorType = VK_DESCRIPTOR_TYPE_STORAGE_BUFFER,
            .descriptorCount = 1,
            .stageFlags = VK_SHADER_STAGE_COMPUTE_BIT,
        },
        {
            .binding = 1,
            .descriptorType = VK_DESCRIPTOR_TYPE_STORAGE_BUFFER,
            .descriptorCount = 1,
            .stageFlags = VK_SHADER_STAGE_COMPUTE_BIT,
        },
    };
    VkDescriptorSetLayoutCreateInfo settlement_ci = {
        .sType = VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_CREATE_INFO,
        .bindingCount = 2,
        .pBindings = settlement_bindings,
    };
    VK_CHECK(vkCreateDescriptorSetLayout(app->device, &settlement_ci, NULL,
                                         &app->settlement_layout));

    for (uint32_t i = 0; i < app->market_count; i++) {
        MarketBook *m = &app->markets[i];
        VkDescriptorSetLayoutBinding market_bindings[2] = {
            {
                .binding = 0,
                .descriptorType = VK_DESCRIPTOR_TYPE_STORAGE_BUFFER,
                .descriptorCount = m->storage_count,
                .stageFlags = VK_SHADER_STAGE_COMPUTE_BIT,
            },
            {
                .binding = 1,
                .descriptorType = VK_DESCRIPTOR_TYPE_INLINE_UNIFORM_BLOCK,
                .descriptorCount = m->memo_bytes,
                .stageFlags = VK_SHADER_STAGE_COMPUTE_BIT,
            },
        };
        VkDescriptorSetLayoutCreateInfo market_ci = {
            .sType = VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_CREATE_INFO,
            .bindingCount = m->memo_bytes ? 2u : 1u,
            .pBindings = market_bindings,
        };
        VK_CHECK(vkCreateDescriptorSetLayout(app->device, &market_ci, NULL,
                                             &m->layout));
    }
}

static void create_settlement_pipeline(App *app) {
    VkPushConstantRange pcr = {
        .stageFlags = VK_SHADER_STAGE_COMPUTE_BIT,
        .offset = 0,
        .size = sizeof(Push),
    };
    VkPipelineLayoutCreateInfo plci = {
        .sType = VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO,
        .setLayoutCount = 1,
        .pSetLayouts = &app->settlement_layout,
        .pushConstantRangeCount = 1,
        .pPushConstantRanges = &pcr,
    };
    VK_CHECK(vkCreatePipelineLayout(app->device, &plci, NULL, &app->pipe_layout));

    VkShaderModuleCreateInfo smci = {
        .sType = VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO,
        .codeSize = sizeof(shader_spv),
        .pCode = shader_spv,
    };
    VkShaderModule shader;
    VK_CHECK(vkCreateShaderModule(app->device, &smci, NULL, &shader));

    VkComputePipelineCreateInfo cpci = {
        .sType = VK_STRUCTURE_TYPE_COMPUTE_PIPELINE_CREATE_INFO,
        .stage = {
            .sType = VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO,
            .stage = VK_SHADER_STAGE_COMPUTE_BIT,
            .module = shader,
            .pName = "main",
        },
        .layout = app->pipe_layout,
    };
    VK_CHECK(vkCreateComputePipelines(app->device, VK_NULL_HANDLE, 1, &cpci,
                                      NULL, &app->pipeline));
    vkDestroyShaderModule(app->device, shader, NULL);
}

static void open_order_books(App *app) {
    VkDescriptorPoolSize sizes[2] = {
        {
            .type = VK_DESCRIPTOR_TYPE_STORAGE_BUFFER,
            .descriptorCount = 3 + app->outcome_slot_total,
        },
        {
            .type = VK_DESCRIPTOR_TYPE_INLINE_UNIFORM_BLOCK,
            .descriptorCount = QUOTE_MEMO_BYTES + app->memo_byte_total,
        },
    };
    VkDescriptorPoolCreateInfo dpci = {
        .sType = VK_STRUCTURE_TYPE_DESCRIPTOR_POOL_CREATE_INFO,
        .maxSets = 2 + app->market_count,
        .poolSizeCount = 2,
        .pPoolSizes = sizes,
    };
    VK_CHECK(vkCreateDescriptorPool(app->device, &dpci, NULL, &app->desc_pool));

    VkDescriptorSetLayout layouts[2 + MAX_MARKETS];
    uint32_t n = 0;
    layouts[n++] = app->quote_layout;
    for (uint32_t i = 0; i < app->market_count; i++) {
        layouts[n++] = app->markets[i].layout;
    }
    layouts[n++] = app->settlement_layout;

    VkDescriptorSet sets[2 + MAX_MARKETS];
    VkDescriptorSetAllocateInfo ai = {
        .sType = VK_STRUCTURE_TYPE_DESCRIPTOR_SET_ALLOCATE_INFO,
        .descriptorPool = app->desc_pool,
        .descriptorSetCount = n,
        .pSetLayouts = layouts,
    };
    VK_CHECK(vkAllocateDescriptorSets(app->device, &ai, sets));

    n = 0;
    app->quote_book = sets[n++];
    for (uint32_t i = 0; i < app->market_count; i++) {
        app->markets[i].set = sets[n++];
    }
    app->settlement_book = sets[n++];
}

static void init_resolution(App *app) {
    const char *env = getenv("FLAG");
    if (!env || !*env) {
        env = "UMDCTF{test_flag}";
    }
    snprintf(app->resolution, sizeof(app->resolution), "%s", env);
    size_t resolution_len = strlen(app->resolution) + 1;
    if (resolution_len > RESOLUTION_WORDS * sizeof(uint32_t)) {
        resolution_len = RESOLUTION_WORDS * sizeof(uint32_t);
        app->resolution[resolution_len - 1] = 0;
    }
    app->resolution_words = (uint32_t)((resolution_len + 3) / 4);

    make_raw_buffer(app, &app->oracle_buf, RESOLUTION_WORDS * sizeof(uint32_t));
    memcpy(app->oracle_buf.map, app->resolution, resolution_len);
    make_raw_buffer(app, &app->clearing_buf, RESOLUTION_WORDS * sizeof(uint32_t));
    make_raw_buffer(app, &app->public_quote_buf, 0x100);
}

static void arm(App *app) {
    if (app->armed) {
        puts("exchange already open");
        return;
    }
    if (app->outcome_slot_total < MIN_MARKET_OUTCOME_SLOTS) {
        printf("need at least %u listed outcome slots\n",
               MIN_MARKET_OUTCOME_SLOTS);
        return;
    }

    create_market_layouts(app);
    create_settlement_pipeline(app);
    init_resolution(app);
    open_order_books(app);

    update_storage_desc(app, app->quote_book, 0, 0,
                        app->public_quote_buf.buf, 0, app->public_quote_buf.size);
    update_storage_desc(app, app->settlement_book, 0, 0,
                        app->oracle_buf.buf, 0, app->oracle_buf.size);
    update_storage_desc(app, app->settlement_book, 1, 0,
                        app->clearing_buf.buf, 0, app->clearing_buf.size);

    app->armed = true;
    puts("exchange open");
}

static void menu_list_market(App *app) {
    if (app->armed) {
        puts("exchange is open");
        return;
    }
    if (app->market_count == MAX_MARKETS) {
        puts("full");
        return;
    }

    uint64_t storage = ask_u64("outcome_slots: ");
    uint64_t memo_bytes = ask_u64("memo_bytes: ");
    if (storage < 1 || storage > MAX_MARKET_OUTCOME_SLOTS) {
        puts("bad outcome slot count");
        return;
    }
    if (memo_bytes > MAX_MARKET_MEMO_BYTES || (memo_bytes & 3)) {
        puts("bad memo byte count");
        return;
    }

    MarketBook *m = &app->markets[app->market_count];
    m->storage_count = (uint32_t)storage;
    m->memo_bytes = (uint32_t)memo_bytes;
    app->outcome_slot_total += m->storage_count;
    app->memo_byte_total += m->memo_bytes;

    printf("market id: %u\n", app->market_count);
    app->market_count++;
}

static void menu_open_account(App *app) {
    if (app->armed) {
        puts("exchange is open");
        return;
    }

    int slot = -1;
    for (int i = 0; i < MAX_ACCOUNTS; i++) {
        if (!app->accounts[i].used) {
            slot = i;
            break;
        }
    }
    if (slot < 0) {
        puts("full");
        return;
    }

    uint64_t size = ask_u64("bytes: ");
    if (size < 4 || size > MAX_ACCOUNT_SIZE) {
        puts("bad size");
        return;
    }
    size = (size + 3) & ~3ull;

    RawBuf raw;
    make_raw_buffer(app, &raw, size);
    app->accounts[slot] = (AccountBuf){
        .used = true,
        .buf = raw.buf,
        .mem = raw.mem,
        .map = raw.map,
        .size = raw.size,
    };
    printf("account: %d\n", slot);
}

static void menu_fund_account(App *app) {
    uint64_t id = ask_u64("account: ");
    uint64_t off = ask_u64("offset: ");
    if (id >= MAX_ACCOUNTS || !app->accounts[id].used) {
        puts("bad account");
        return;
    }

    char line[MAX_HEX_WRITE * 2 + 64];
    uint8_t bytes[MAX_HEX_WRITE];
    size_t len = 0;
    printf("hex: ");
    if (!read_line(line, sizeof(line))) {
        exit(0);
    }
    if (parse_hex(line, bytes, sizeof(bytes), &len) < 0) {
        puts("bad hex");
        return;
    }

    AccountBuf *b = &app->accounts[id];
    if (off > b->size || len > b->size - off) {
        puts("out of bounds");
        return;
    }
    memcpy(b->map + off, bytes, len);
    puts("written");
}

static void menu_audit_account(App *app) {
    uint64_t id = ask_u64("account: ");
    uint64_t off = ask_u64("offset: ");
    uint64_t len = ask_u64("bytes: ");
    if (id >= MAX_ACCOUNTS || !app->accounts[id].used) {
        puts("bad account");
        return;
    }
    AccountBuf *b = &app->accounts[id];
    if (len > 0x200 || off > b->size || len > b->size - off) {
        puts("out of bounds");
        return;
    }
    for (uint64_t i = 0; i < len; i++) {
        printf("%02x", b->map[off + i]);
    }
    puts("");
}

static void menu_quote_position(App *app) {
    if (!app->armed) {
        puts("exchange closed");
        return;
    }
    if (app->quoted) {
        puts("quote already accepted");
        return;
    }

    uint64_t idx = ask_u64("price_index: ");
    uint64_t id = ask_u64("account: ");
    uint64_t off = ask_u64("offset: ");
    uint64_t range = ask_u64("range: ");
    if (idx < MIN_PRICE_INDEX || idx > MAX_PRICE_INDEX) {
        puts("bad price index");
        return;
    }
    if (id >= MAX_ACCOUNTS || !app->accounts[id].used) {
        puts("bad account");
        return;
    }
    AccountBuf *b = &app->accounts[id];
    if (range < 4 || off > b->size || range > b->size - off) {
        puts("bad range");
        return;
    }

    update_storage_desc(app, app->quote_book, 0, (uint32_t)idx,
                        b->buf, off, range);
    app->quoted = true;
    puts("quoted");
}

static void settle_round(App *app, uint32_t word) {
    VK_CHECK(vkResetCommandPool(app->device, app->cmd_pool, 0));

    VkCommandBufferBeginInfo begin = {
        .sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO,
        .flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT,
    };
    VK_CHECK(vkBeginCommandBuffer(app->cmd, &begin));
    vkCmdBindPipeline(app->cmd, VK_PIPELINE_BIND_POINT_COMPUTE, app->pipeline);
    vkCmdBindDescriptorSets(app->cmd, VK_PIPELINE_BIND_POINT_COMPUTE,
                            app->pipe_layout, 0, 1, &app->settlement_book, 0, NULL);
    Push push = {
        .mode = 0,
        .index = word,
        .value = 0,
    };
    vkCmdPushConstants(app->cmd, app->pipe_layout, VK_SHADER_STAGE_COMPUTE_BIT,
                       0, sizeof(push), &push);
    vkCmdDispatch(app->cmd, 1, 1, 1);
    VK_CHECK(vkEndCommandBuffer(app->cmd));

    VkSubmitInfo submit = {
        .sType = VK_STRUCTURE_TYPE_SUBMIT_INFO,
        .commandBufferCount = 1,
        .pCommandBuffers = &app->cmd,
    };
    VK_CHECK(vkQueueSubmit(app->queue, 1, &submit, VK_NULL_HANDLE));
    VK_CHECK(vkQueueWaitIdle(app->queue));
}

static void menu_settle(App *app) {
    if (!app->armed) {
        puts("exchange closed");
        return;
    }
    uint64_t word = ask_u64("round: ");
    if (word >= app->resolution_words || word >= RESOLUTION_WORDS) {
        puts("bad round");
        return;
    }
    settle_round(app, (uint32_t)word);
    puts("settled");
}

static void print_menu(void) {
    puts("");
    puts("1. open_account(bytes)");
    puts("2. fund_account(account, offset, hex)");
    puts("3. audit_account(account, offset, bytes)");
    puts("4. list_market(outcome_slots, memo_bytes)");
    puts("5. open_exchange()");
    puts("6. quote_position(price_index, account, offset, range)");
    puts("7. settle_market(round)");
    puts("0. quit");
}

static void banner(App *app) {
    puts("vkexchange");
    printf("device: %s\n", app->props.deviceName);
}

int main(void) {
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);

    App app;
    init_vulkan(&app);
    banner(&app);

    for (;;) {
        print_menu();
        uint64_t c = ask_u64("> ");
        switch (c) {
        case 1:
            menu_open_account(&app);
            break;
        case 2:
            menu_fund_account(&app);
            break;
        case 3:
            menu_audit_account(&app);
            break;
        case 4:
            menu_list_market(&app);
            break;
        case 5:
            arm(&app);
            break;
        case 6:
            menu_quote_position(&app);
            break;
        case 7:
            menu_settle(&app);
            break;
        case 0:
            return 0;
        default:
            puts("?");
            break;
        }
    }
}
