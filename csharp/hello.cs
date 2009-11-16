// hello -- a very simple C# program

// Concepts:
//  1. Everything goes into a class.
//  2. The `using' keyword splices namespaces together.
//  3. A `static void Main()' method is the program's entry point.
//  4. `System.Console' is an abstraction of a terminal.
//     (a) `In', `Out', and `Error' are System.IO.TextWriter objects.

using System;

class Cat
{
	static void Main(string[] argv)
	{
		Console.WriteLine("Hello, world!");
	}
}
