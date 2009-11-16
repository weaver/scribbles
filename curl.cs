// curl -- copy a URL to standard output

// Concepts:
//  1. The System.Net namespace contains implementations for many
//     standard network protocols.
//  2. A request for a URI can be created using `WebRequest.Create()'.
//  3. Response headers are in something like a dictionary.
//  4. Response data can be read from a Stream.

using System;
using System.IO;
using System.Net;

class cURL
{
	const int BUFFER_SIZE = 1024;
	private static char[] BUFFER = new char[BUFFER_SIZE];
	
	static int Main(string[] argv)
	{
		if (argv.Length != 1) {
			usage();
			return 1;
		}

		using(HttpWebResponse response = get(argv[0])) {
			write(response);
		}

		return 0;
	}

	static void usage()
	{
		Console.Error.WriteLine("usage: curl <uri>");
	}

	static HttpWebResponse get(string uri)
	{
		WebRequest request = WebRequest.Create(uri);
		return (HttpWebResponse)request.GetResponse();
	}

	static void write(HttpWebResponse response)
	{
		write(response.Headers);
		
		using (Stream data = response.GetResponseStream()) {
			using (TextReader port = new StreamReader(data)) {
				write(port);
			}
		}
	}

	static void write(WebHeaderCollection headers)
	{
		for (int index = 0; index < headers.Count; index++) {
			Console.WriteLine("{0}: {1}", headers.Keys[index], headers[index]);
		}
		Console.WriteLine("");
	}

	static void write(TextReader port)
	{
		int bytes;
		
		while(0 != (bytes = port.Read(BUFFER, 0, BUFFER_SIZE))) {
			Console.Write(BUFFER, 0, bytes);
		}
	}	
}