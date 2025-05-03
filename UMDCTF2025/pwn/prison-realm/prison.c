#include <signal.h>
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>

// 閉門
void gate_close() {
  exit(1);
}

// Will you get stuck in the prison realm?
//
//
// 獄門疆 開門  
__attribute__((constructor))
void prison_realm_open() {
  setvbuf(stdout, NULL, _IONBF, 0);
  setvbuf(stdin, NULL, _IONBF, 0);
  signal(SIGALRM, gate_close);
  alarm(60);
}

int main() {

  // Geto steps out from behind the activated prison realm...
  char barrier_dimension_realm[30];
  fgets(barrier_dimension_realm, 300, stdin);
}
