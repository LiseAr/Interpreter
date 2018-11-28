int main(int max, int incr)
{
	int i;
	for (i = 1; i < max; i = i + incr)
	{
		int cafunfo;
		cafunfo = (!(i % 7));
		if (!cafunfo)
		{
			int n;
			cafunfo = 0;
			n = i;
			while (n > 0)
			{
				if (n % 10 == 7)
				{
					cafunfo = 1;
					break;
				}
				n = n / 10;
			}
		}

		if (cafunfo)
			print("cafunfo ");
		else
			print(i, " ");

		if (!(i % 20))
			print("\n");
	}
}

