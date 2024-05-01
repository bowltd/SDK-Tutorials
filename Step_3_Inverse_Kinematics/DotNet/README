KNOWN ISSUES:

Ubuntu 20.04

Description:
There is a known issue with OpenCvSharp4_.runtime.ubuntu.20.04-x64 installing runtime into bin/Debug/net8.0/runtimes/ubuntu.20.04-x64/native instead of bin/Debug/net8.0/runtimes/linux-x64/native where it can be picked automatically

Unhandled exception. System.TypeInitializationException: The type initializer for 'OpenCvSharp.Internal.NativeMethods' threw an exception.
 ---> System.DllNotFoundException: Unable to load shared library 'OpenCvSharpExtern' or one of its dependencies. In order to help diagnose loading problems, consider using a tool like strace. If you're using glibc, consider setting the LD_DEBUG environment variable:
/home/daniel/Projects/Version3/Tutorials/SDK-Tutorials/Step_1_Vision/.NET/Bow_Tutorial_1/Bow_Tutorial_1/bin/Debug/net8.0/runtimes/linux-x64/native/OpenCvSharpExtern.so: cannot open shared object file: No such file or directory
/usr/share/dotnet/shared/Microsoft.NETCore.App/8.0.4/OpenCvSharpExtern.so: cannot open shared object file: No such file or directory
/home/daniel/Projects/Version3/Tutorials/SDK-Tutorials/Step_1_Vision/.NET/Bow_Tutorial_1/Bow_Tutorial_1/bin/Debug/net8.0/runtimes/linux-x64/native/libOpenCvSharpExtern.so: cannot open shared object file: No such file or directory
/usr/share/dotnet/shared/Microsoft.NETCore.App/8.0.4/libOpenCvSharpExtern.so: cannot open shared object file: No such file or directory
/home/daniel/Projects/Version3/Tutorials/SDK-Tutorials/Step_1_Vision/.NET/Bow_Tutorial_1/Bow_Tutorial_1/bin/Debug/net8.0/runtimes/linux-x64/native/OpenCvSharpExtern: cannot open shared object file: No such file or directory
/usr/share/dotnet/shared/Microsoft.NETCore.App/8.0.4/OpenCvSharpExtern: cannot open shared object file: No such file or directory
/home/daniel/Projects/Version3/Tutorials/SDK-Tutorials/Step_1_Vision/.NET/Bow_Tutorial_1/Bow_Tutorial_1/bin/Debug/net8.0/runtimes/linux-x64/native/libOpenCvSharpExtern: cannot open shared object file: No such file or directory
/usr/share/dotnet/shared/Microsoft.NETCore.App/8.0.4/libOpenCvSharpExtern: cannot open shared object file: No such file or directory


Fix: Navigate to bin/Debug/net8.0/runtimes/ubuntu.20.04-x64/native and copy libOpenCvSharpExtern.so to bin/Debug/net8.0/runtimes/linux-x64/native