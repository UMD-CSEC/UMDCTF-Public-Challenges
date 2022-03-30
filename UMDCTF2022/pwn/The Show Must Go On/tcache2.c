#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <crypt.h> 

#define MAX_ACTS 16

void win();
void tellAJoke(); 
void *malloc_set(size_t size); 
char *showDescription = NULL; 
typedef struct Act {
    char name[0x20];
    char actCode[0x40];
    void (*performAct)();
} Act;

char *message1;
char *message2;
char *message3;
char salt[0x10] = "UMD_15_Th3_B35T\0";
char *jokes[] = {
    "testing1",
    "testing2", 
    "testing3"
};
Act *mainAct;
Act *currentAct;
Act *actList[MAX_ACTS]; 


void win()
{
    char *fileContents = malloc_set(0x20); 
    FILE *file = NULL;
    
    if ((file = fopen("flag.txt", "r")) == NULL)
    {
        printf("Couldn't read flag file"); 
        return;
    }
    
    fscanf(file, "%s", fileContents);
    
    printf("%s\n", fileContents); 

    fclose(file);
    
    return; 
        
}

void tellAJoke()
{
    srand(time(NULL)); 
    int r = rand() % 3;

    printf("Here we go!\n");
    printf("%s\n", jokes[r]);    
}

void* malloc_set(size_t size)
{
    void *ret = malloc(size);
    memset(ret, 0, size);
    return ret;
}

void newAct()
{
    Act *newAct = malloc_set(sizeof(Act));
    char actCode[0x40];  
    char *actCodeCrypt = malloc_set(0x40); 
    printf("Name of Act: ");
    scanf("%s", newAct->name);
    
    printf("Act Code: ");
    scanf("%s", actCode);
    
    actCodeCrypt = crypt(actCode, salt); 

    memcpy(newAct->actCode, actCodeCrypt, 0x40);

    newAct->performAct = tellAJoke; 

    for (int i = 0; i < MAX_ACTS; i++)
    {
        if (strnlen(actList[i]->name, 0x20) == 0)
        {
            actList[i] = newAct;
            currentAct = actList[i]; 
            break; 
        }
    }
}

void switchAct()
{
    char name[0x20];
    char actCode[0x40];
    char *actCodeCrypt;

    printf("Name of Act: ");
    scanf("%s", name);
    
    printf("Act Code: ");
    scanf("%s", actCode);

    actCodeCrypt = crypt(actCode, salt);   
    
    for (int i = 0; i < MAX_ACTS; i++)
    {
        if (strncmp(actList[i]->name, name, 0x20) == 0 && strncmp(actList[i]->actCode, actCodeCrypt, 0x40) == 0)
        {
            currentAct = actList[i];    
        }
    }
}


int whatToDo() 
{
    printf("What would you like to do?\n"); 
    int action = 0, endShow = 0;
        
    printf("+-------------+\n");
    printf("|   Actions   |\n");
    printf("|-------------|\n");
    printf("| Perform Act |\n");
    printf("| Switch Act  |\n");
    printf("| End Show    |\n");
    printf("+-------------|\n");
    printf("Action: ");

    scanf("%d", &action);
    
    switch (action)
    {
        case 1:
            currentAct->performAct();
            break;
        case 2:
            switchAct();
            printf("I think the current act switched switched. It might appear when we start up again...\n");
            break;
        case 3:
            endShow = 1; 
            break;
    }
    return endShow;
}


int setup()
{
    char actName[0x20];
    char *actCode = NULL;
    int descLen = 0;  
    message1 = malloc_set(0x50);
    message2 = malloc_set(0x60);                            
    message3 = malloc_set(0x80);                            
                                                                  
    strncpy(message1, "Welcome to the comedy club!\n", 28);       
    strncpy(message2, "We only have the best comedians here!\n", 37); 
    strncpy(message3, "Please help us set up for your act\n", 36);

    printf("%s", message1);
    printf("%s", message2);
    printf("%s", message3); 

    printf("What is the name of your act?\n");
    scanf("%s", actName); 

    mainAct = malloc_set(sizeof(Act));
    strncpy(mainAct->name, actName, 0x20); 
    actCode = crypt("Main_Act_Is_The_Best", salt);
    strncpy(mainAct->actCode, actCode, 0x40); 
    printf("Your act code is: Main_Act_Is_The_Best\n"); 
    mainAct->performAct = tellAJoke;
    currentAct = mainAct;
    
    free(message1);
    free(message3);

    printf("How long do you want the show description to be?\n");
    scanf("%d", &descLen);
    showDescription = malloc_set(descLen+8);
    printf("Describe the show for us:\n"); 
    getchar();
    fgets(showDescription, 500, stdin);  

    actList[0] = mainAct;

    return 0;
}

void main()
{
    setbuf(stdout, 0);
    setbuf(stdin, 0);
    setbuf(stderr, 0);

    setup();
    int endShow = whatToDo();
    if (endShow)
    {
        printf("The show is over, goodbye!\n");
    }
        
}
