#include <stdio.h>
void foo(const char *str) {
    printf("Hello : %s\n", str);
}

int main() {
    const char *str = "bar";
    foo(str);
    return 0;
}
