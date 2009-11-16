// cat -- concatenate files into standard output

// Concepts:
//  1. A character buffer can be declared statically in a class
//     definition.
//  2. Command-line arguments can be iterated over using `foreach'.
//  3. System.IO.TextReader is an abstract base class; StreamReader is
//     an implementation.
//  4. Implicit conversion of `int' to `bool' is not allowed in
//     conditions.
//  5. An Exception has a Message property with a brief summary of the
//     error.

using System;
using System.IO;

class Cat
{
	const int bufferSize = 1024;
	private static char[] buffer = new char[bufferSize];

	static int Main(string[] argv)
	{
		if (argv.Length == 0) {
			write(Console.In);
			return 0;
		}
		
		try {
			write(argv);
		}
		catch (FileNotFoundException ex) {
			Console.Error.WriteLine("cat: {0}", ex.Message);
			return 1;
		}

		return 0;
	}

	static void write(string[] paths)
	{
		foreach (string path in paths) {
			write(path);
		}		
	}

	static void write(string path)
	{
		using(TextReader port = new StreamReader(path)) {
			write(port);
		}
	}

	static void write(TextReader port)
	{
		int bytes;
		
		while(0 != (bytes = port.Read(buffer, 0, bufferSize))) {
			Console.Write(buffer, 0, bytes);
		}
	}
}