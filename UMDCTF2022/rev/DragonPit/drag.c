#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main()
{
	char response[21];
	printf("When should Fred jump into the dragon pit? \n");
	fgets(response, 21, stdin);

	int x = 6;
	int y = 3;
	int z = 2;
	int a = 13;
	char expected[] = {'w','h','0','n','T','h','e','D','r','0','g','s','H','P','i','s','0','0','0','0',0};
	expected[2] = (char)((z*z*a)-(z/z));
	expected[9] = (char)(z*z*a);
	expected[16] = (char)(49);
	expected[18] = (char)(z*z*a);
	expected[19] = (char)((z*z*a)+z*z);
	if ( strcmp(response, expected) == 0)
	{
		char flag[] = {'U','M','D','C','T','F','{','B','l','u','S','t','0','X','X','X','X','X','X','X'};
		flag[19] = '}';
		flag[18] = 'g';
		flag[17] = response[9];
		flag[16] = 'r';
		flag[15] = 'd';
		flag[14] = (char)((z*z*a)-(z/z));
		flag[13] = 'l';
		printf("%.20s\n", flag);
	} else 
	{
		char sneaky[] = "Developer's Notes: Strings won't work here, try ghdira";
		char sneaky2[] = "Say no to League of Legends kids";
		printf("You waited too long! \n");
		printf("Red Team has slain the Dragon! \n");
		printf("An Ally has been slain! \n");
	}
	return 0;
}