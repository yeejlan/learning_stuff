        if(oSession.HostnameIs("10.2.10.100")){
          oSession.oResponse.headers.Remove("Cache-Control");
            oSession.oResponse.headers.Remove("Pragma");
            oSession.oResponse.headers["Last-Modified"] = "Thu, 01 Jan 2020 01:01:01 GMT";
            oSession.oResponse.headers["Expires"] = "Thu, 01 Jan 2050 01:01:01 GMT";
        }