#include <stdlib.h>
#include <stdio.h>
#include <time.h>

int main() {
  srand(time(0));

  for (int i = 0; i < 6; i++) {
    printf("%d\n", rand());
  }
}

