Chromium Embedded Framework (CEF) Standard Binary Distribution for Windows
-------------------------------------------------------------------------------

Date:             March 14, 2014

CEF Version:      3.1650.1639
CEF URL:          http://chromiumembedded.googlecode.com/svn/branches/1650/cef3@1639

Chromium Verison: 31.0.1650.57
Chromium URL:     http://src.chromium.org/svn/branches/1650/src@235101

This distribution contains all components necessary to build and distribute an
application using CEF on the Windows platform. Please see the LICENSING
section of this document for licensing terms and conditions.


CONTENTS
--------

cefclient   Contains the cefclient sample application configured to build
            using the files in this distribution.

Debug       Contains libcef.dll, libcef.lib and other components required to
            build and run the debug version of CEF-based applications. By
            default these files should be placed in the same directory as the
            executable and will be copied there as part of the build process.

include     Contains all required CEF header files.

libcef_dll  Contains the source code for the libcef_dll_wrapper static library
            that all applications using the CEF C++ API must link against.

Release     Contains libcef.dll, libcef.lib and other components required to
            build and run the release version of CEF-based applications. By
            default these files should be placed in the same directory as the
            executable and will be copied there as part of the build process.

Resources   Contains resources required by libcef.dll. By default these files
            should be placed in the same directory as libcef.dll. By default
            these files should be placed in the same directory as libcef.dll
            and will be copied there as part of the build process.


USAGE
-----

Visual Studio 2012 and Visual Studio 2010:
  Open the cefclient2010.sln solution in Visual Studio and build.

Visual Studio 2008:
  Open the cefclient2008.sln solution in Visual Studio and build.

Visual Studio 2005:
  1. Open the cefclient.vcproj and libcef_dll_wrapper.vcproj files in a text
     editor. Change Version="9.00" to Version="8.00".
  2. Open the cefclient2005.sln file in a text editor. Change "Version 9.00" to
     "Version 8.00".
  3. Open the cefclient2005.sln solution in Visual Studio and build.

Please visit the CEF Website for additional usage information.

http://code.google.com/p/chromiumembedded


REDISTRIBUTION
--------------

This binary distribution contains the below components. Components listed under
the "required" section must be redistributed with all applications using CEF.
Components listed under the "optional" section may be excluded if the related
features will not be used.

Required components:

* CEF core library
    libcef.dll

* Unicode support
    icudt.dll

Optional components:

* Localized resources
    locales/
  Note: Contains localized strings for WebKit UI controls. A .pak file is loaded
  from this folder based on the CefSettings.locale value. Only configured
  locales need to be distributed. If no locale is configured the default locale
  of "en-US" will be used. Locale file loading can be disabled completely using
  CefSettings.pack_loading_disabled. The locales folder path can be customized
  using CefSettings.locales_dir_path.

* Other resources
    cef.pak
    devtools_resources.pak
  Note: Contains WebKit image and inspector resources. Pack file loading can be
  disabled completely using CefSettings.pack_loading_disabled. The resources
  directory path can be customized using CefSettings.resources_dir_path.

* FFmpeg audio and video support
    ffmpegsumo.dll
  Note: Without this component HTML5 audio and video will not function.

* Angle and Direct3D support
    d3dcompiler_43.dll (required for Windows XP)
    d3dcompiler_46.dll (required for Windows Vista and newer)
    libEGL.dll
    libGLESv2.dll
  Note: Without these components HTML5 accelerated content like 2D canvas, 3D
  CSS and WebGL will not function.


LICENSING
---------

The CEF project is BSD licensed. Please read the LICENSE.txt file included with
this binary distribution for licensing terms and conditions. Other software
included in this distribution is provided under other licenses. Please visit
"about:credits" in a CEF-based application for complete Chromium and third-party
licensing information.
