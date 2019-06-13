#include <stdio.h>

#define NAMESIZE 512
#define JOBSIZE 512

typedef struct {
    char name[NAMESIZE];
    char sex;
} Person;

typedef struct {
    Person person;
    char *job;
} Employee;


void hello(Person *p)
{
    printf("Hello World\n");
    printf("%s\n", p[0].name);
    printf("%c\n", p[0].sex);
    //printf("%s\n", p->job);
    printf("%s\n", p[1].name);
    printf("%c\n", p[1].sex);
}

#define name person.name
#define sex person.sex

int main()
{
    Employee e[2] = {
        {"Jerry", '65'},
        {"Test123", '67'}
    };
    printf("%d, %d\n", sizeof(Person), sizeof(Employee));
    hello(e);
    return 0;
}