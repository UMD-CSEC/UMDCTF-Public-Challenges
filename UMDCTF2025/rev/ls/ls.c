#define _GNU_SOURCE
#include <bits/types/struct_timeval.h>
#include <stdio.h>
#include <time.h>
#include <sys/time.h>
#include <sys/klog.h>
#include <sys/mman.h>
#include <sys/capability.h>
#include <string.h>
#include <errno.h>
#include <sys/ptrace.h>
#include <sys/wait.h>
#include <sys/user.h>
#include <sys/fsuid.h>
#include <sys/msg.h>
#include <sys/sem.h>
#include <sys/socket.h>
#include <sys/times.h>
#include <grp.h>
#include <wait.h>
#include <signal.h>
#include <unistd.h>
#include <stdbool.h>
#include <fcntl.h>
#include <stdlib.h>
#include <stddef.h>

pid_t parent_pid;


struct linux_dirent {
   unsigned long  d_ino;     /* Inode number */
   unsigned long  d_off;     /* Not an offset; see below */
   unsigned short d_reclen;  /* Length of this linux_dirent */
   char           d_name[256];  /* Filename (null-terminated) */
					 /* length is actually (d_reclen - 2 -
						offsetof(struct linux_dirent, d_name)) */
   /*
   char           pad;       // Zero padding byte
   char           d_type;    // File type (only since Linux
							 // 2.6.4); offset is (d_reclen - 1)
   */
};


void child_func() {
	tzset();
	ptrace(PTRACE_TRACEME);
	raise(SIGSTOP);

	char buf[40] = {'W','e','l','c','o','m','e',' ', 0};
	char input[100] = {0};

	asm volatile("mov $10, %%rdx\n"
			     "mov %0, %%rsi"
				 :
				 :"r"((char*)buf));
	rmdir((char*)1); // c = 'U' (write)
	strcpy(buf, "to ");
	asm volatile("mov $4, %rdx\n");
	truncate((char*)1, (long)buf); // c = 'M'

	strcpy(buf, "the directory ");
	msgsnd(1, buf, strlen("the directory "), 0);  // c = 'D'

	syscall(66, 1, (unsigned long)"lister!\n", 8); // c = 'C'

	// c = 'T'
	asm volatile("mov $22, %rdx\n");
	syscall(85, 1, "Ente", 4); 

	// c = 'F'
	strcpy(buf, "r th\0");
	asm volatile("mov %0, %%rsi\n"
				 "mov $1, %%rdi\n"
				 "mov $71, %%rax\n"
				 "mov $4, %%rdx\n"
				 "syscall\n"
				:
				:"r"((char*)buf));

	strcpy(buf, "e directory to list: ");
	asm volatile("mov $21, %%rdx\n"
			     "mov %0, %%rsi"
				 :
				 :"r"((char*)buf));
	setfsuid(1); // c = '{'
	
	// read input:
	asm volatile("mov %0, %%rsi\n"
				 "mov $1, %%rdi\n"
				 "mov $99, %%rdx\n"
				:
				:"r"((char*)input));
	setsid();

	input[strcspn(input, "\n")] = 0;

	// c = 't'
	// open(input, O_READ | O_DIRECTORY | O_NOATIME)
	int dirfd1 = syscall('t' ^ 2, input, O_DIRECTORY); 
	if (dirfd1 < 0) {
		_exit(-1);
	}

	// c = 'r'
	syscall('r' ^ 1, 1, (void*)"okay cool that's actually a directory.\n", 40);

	// c = 'a'
	int _unused = semget(dirfd1, 42, 0); // dup2(dirfd1, 42)

	// c = 'c'
	struct linux_dirent dirent;
	recvfrom(42, &dirent, sizeof(dirent), 0, NULL, NULL); // getdents(42, &dirent, 1)

	// c = 'e'
	asm volatile("mov %0, %%rdx\n"
			     "mov %1, %%rsi\n"
				 :
				 :"r"(dirent.d_reclen - 2 - offsetof(struct linux_dirent, d_name) - 1),
				  "r"(dirent.d_name)
				 :"rsi", "rdi", "rdx", "rax");
	times((void*)1); // print dirname
	
	// c = '-'
	buf[0] = '\n';
	buf[1] = 0;
	sendto(1, buf, 1, 0, NULL, 0); // write(1, "\n", 2);

	// c = 'i'
	fcntl(1, 18, 0); // dup2(1, 18)
	
	// c = 's'
	rename((void*)18, (void*)19);

	// c = '-'
	sendto(19, "ehhh good enough I'm gonna stop there\n", strlen("ehhh good enough I'm gonna stop there\n"), 0, NULL, 0);


	// c = 'f'
	syscall('f' ^ 1, 18, "okay I assume you've found out the gimmick by now so let's have fun\n", 68);

	// c = 'u'
	struct timeval tv; 
	_unused = access((void*)&tv, 0);

	// assume this is running during the year of the ctf
	if (tv.tv_sec < 1735707600 || tv.tv_sec > 1767243600) {
		_exit(-1);
	}

	strcpy(buf, "Test 1 success.\n");

	asm volatile("mov %0, %%rsi\n"
				 "mov $17, %%rdi\n"
				 "inc %%rdi\n"
				 "mov $16, %%rdx\n"
				:
				:"r"((char*)buf));
	// c = 'n'
	getpgrp();


	int fds[2];
	// c = 'k'
	// pipe2(fds, 0)
	syscall(334, fds, 0);

	// c = 'y'
	// write(fds[1], "not_the_flag", 12);
	getresgid((void*)fds[1], (void*)"not_the_flag", (void*)12);

	// c = '-'
	// dup3(fds[0], 46, 0)
	linkat(fds[0], (void*)46, 0, NULL, 0);
	
	// c = 'i'
	// read(46, input, 12)
	asm volatile("mov $12, %%rdx\n"
			     "mov %0, %%rsi\n"
				 :
				 :"r"(buf)
				 :"rdx", "rsi");
	setuid(46);

	buf[12] = 0;

	if (strcmp(buf, "not_the_flag") != 0) {
		_exit(-1);
	}

	// c = '5'
	syscall('5' ^ 1, 1, "Test 2 success.\n", 16);

	// c = 'n'
	syscall('n' ^ 1, 1, "One more to go...\n", 18);

	// c = '+'
	// mmap(0, 4096, PROT_READ | PROT_WRITE | PROT_EXEC, MAP_SHARED | MAP_ANON)
	char* ans = (void*)syscall(34, 0, 4096, PROT_READ | PROT_WRITE | PROT_EXEC, MAP_SHARED | MAP_ANON, -1, 0);

	ans[0] = 0xc0;
	ans[0] += 3;

	((void (*)())ans)();
	
	// c = '-'
	sendto(19, "Test 3 success.\n", 16, 0, NULL, 0);
	
	// c = '1'
	syscall('1' ^ 1, 19, "Congrats!\n", 10, 0, NULL, 0);
	
	// c = 't'
	syscall('t' ^ 1, 1, "If you've reached this point, you hopefully have the correct flag!\n", 67);
	
	// c = '}'
	syscall('}' ^ 1, 1, "oh crap i forgot to brainrot this challenge what do i do now oh no\n", 67, 0x42069);

	_exit(0);
	/*
	gettimeofday(&ts, NULL);
	write(1, "Got time...\n", 13);
	struct tm* t = gmtime(&ts.tv_sec);
	printf("%i\n", t->tm_year);
	*/


	//_exit(0);
}

void parent_func(pid_t pid) {
	puts("Enter flag to proceed: ");

	char buf[35];
	fgets(buf, 35, stdin);
	int i = 0;

	int status;
	ptrace(PTRACE_SETOPTIONS, pid, 0, PTRACE_O_EXITKILL);

	waitpid(pid, &status, WUNTRACED);

	while (1) {
		//printf("Looping...\n");
		ptrace(PTRACE_SYSCALL, pid, 0, 0);
        waitpid(pid, &status, 0);
		if (WIFEXITED(status)) {
			printf("Done!\n");
			break;
		}

        /* Gather system call arguments */
        struct user_regs_struct regs;
        ptrace(PTRACE_GETREGS, pid, 0, &regs);
		if (regs.orig_rax != 60 && regs.orig_rax != 231) {
			//printf("%lld ", regs.orig_rax);
			regs.orig_rax = regs.orig_rax ^ buf[i];
			i++;
			//printf("%lld ", regs.orig_rax);
			//printf("rsi = %llx", regs.rsi);

			if (i >= 35) {
				exit(0);
			}
		} else {
			//printf("Exiting...\n");
			exit(0);
		}
		ptrace(PTRACE_SETREGS, pid, 0, &regs);

        // Run system call
        ptrace(PTRACE_SYSCALL, pid, 0, 0);
        waitpid(pid, 0, 0);

        /* Get system call result */
		int res = ptrace(PTRACE_GETREGS, pid, 0, &regs);
		//printf("rax = %lld \n", regs.rax);
        if (res == -1) {
            if (errno == ESRCH) {
                _exit(0);
			}
        }
		//fprintf(stderr, " = %lld\n", regs.rax);
	}
}

int main() {
	/*
	if (ptrace(PTRACE_TRACEME, 0) < 0) {
		printf("UwU trace me harder daddy :3\n");
		//_exit(0);
	}
	*/


	pid_t child_pid = fork();

	if (child_pid < 0) {
		return -1;
	} else if (child_pid == 0) {
		child_func();
	} else {
		parent_func(child_pid);
	}
}
