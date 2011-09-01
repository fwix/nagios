<?php
#
# this template is intended to be paired with the check_mongo.py script

$def[0] = "";

foreach ( $DS as $KEY => $VAL ){

  ## OPCOUNTER SECTION
  if(preg_match('/_op$/', "$NAME[$KEY]")) {
    ## This is for the opcounters mode on the get_mongo.py script
    ## variables that end in _op will get routed into here
    $opt[0] = "--vertical-label ops/s --title \"Mongo Operations\" ";
    $def[0] .= rrd::def("var$KEY", $RRDFILE[$KEY], $DS[$KEY], "AVERAGE");
    $def[0] .= rrd::line2("var$KEY", rrd::color($KEY), "$NAME[$KEY]");
    $def[0] .= rrd::gprint("var$KEY", array("LAST", "AVERAGE", "MAX"), "\t%4.0lf");
  } 


  ## CONNECTIONS SECTION
  elseif("$NAME[$KEY]"=="connections") {
    ## This is for the opcounters mode on the get_mongo.py script
    ## variables that equal "connections" will get routed into here
    $opt[0] = "--vertical-label connections --title \"Mongo Connections\" ";
    $def[0] .= rrd::def("var$KEY", $RRDFILE[$KEY], $DS[$KEY], "AVERAGE");
    $def[0] .= rrd::line2("var$KEY", "#0000FF", "$NAME[$KEY]");
    $def[0] .= rrd::gprint("var$KEY", array("LAST", "AVERAGE", "MAX"), "\t%4.0lf");
  }

  ## NETWORK I/O SECTION
  elseif(preg_match('/_net$/', "$NAME[$KEY]")) {
    $opt[0] = "--vertical-label Mbs --title \"Mongo Network I/O\" ";

   if("$NAME[$KEY]"=="bytesOut_net") { 
      $def[0] .= rrd::def("var$KEY", $RRDFILE[$KEY], $DS[$KEY], "AVERAGE");
      $def[0] .= rrd::cdef("bits$KEY", "var$KEY,8,*");
      $def[0] .= rrd::gradient("bits$KEY", 'ffff42', 'ee7318', "$NAME[$KEY]");
      $def[0] .= rrd::gprint("bits$KEY", array("LAST", "AVERAGE", "MAX"), "\t%4.2lf");
    }
    elseif("$NAME[$KEY]"=="bytesIn_net") {
      $def[0] .= rrd::def("var$KEY", $RRDFILE[$KEY], $DS[$KEY], "AVERAGE");
      $def[0] .= rrd::cdef("bits$KEY", "var$KEY,-8,*");
      $def[0] .= rrd::gradient("bits$KEY", 'f0f0f0', '0000a0', "$NAME[$KEY]");
      $def[0] .= rrd::gprint("bits$KEY", array("LAST", "AVERAGE", "MAX"), "\t%4.2lf");
    }
  }

  ## REPLICATION
  elseif("$NAME[$KEY]"=="lag") {
    $opt[0] = "--vertical-label seconds --title \"Mongo Replication Lag\" ";
    $def[0] .= rrd::def("var$KEY", $RRDFILE[$KEY], $DS[$KEY], "AVERAGE");
    $def[0] .= rrd::line2("var$KEY", "#0000FF", "$NAME[$KEY]");
    $def[0] .= rrd::gprint("var$KEY", array("LAST", "AVERAGE", "MAX"), "\t%4.0lf");
  }

  ## MEMORY
  elseif(preg_match('/_mem$/', "$NAME[$KEY]")) {
    $opt[0] = "--vertical-label MB --title \"Mongo Memory Usage\" ";
    $def[0] .= rrd::def("var$KEY", $RRDFILE[$KEY], $DS[$KEY], "AVERAGE");
    $def[0] .= rrd::line2("var$KEY", rrd::color($KEY), "$NAME[$KEY]");
    $def[0] .= rrd::gprint("var$KEY", array("LAST", "AVERAGE", "MAX"), "\t%4.0lf");
  }
}

?>
