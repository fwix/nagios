<?php
#
# template file for pnp4nagios
# pairs with the get_network_stats.py script
#

$def[0] = "";
$opt[0] = "--vertical-label bits --title \"Network I/O $servicedesc\" ";


foreach ( $DS as $KEY => $VAL ){
  if(preg_match('/_rx_bytes$/', "$NAME[$KEY]")) {
    $def[0] .= rrd::def("var$KEY", $RRDFILE[$KEY], $DS[$KEY], "AVERAGE");

    # we want to graph this along the negative axis and convert to bits. So
    # we multiply by -8. In order to use this value later on, we set the variable
    # of "rx$KEY" for it
    $def[0] .= rrd::cdef("rx$KEY", "var$KEY,-8,*");

    $def[0] .= rrd::gradient("rx$KEY", 'f0f0f0', '0000a0', "$NAME[$KEY]");
    $def[0] .= rrd::gprint("rx$KEY", array("LAST", "AVERAGE", "MAX"), "\t%4.2lf");
  } 
  elseif(preg_match('/_tx_bytes$/', "$NAME[$KEY]")) {
    $def[0] .= rrd::def("var$KEY", $RRDFILE[$KEY], $DS[$KEY], "AVERAGE");
    $def[0] .= rrd::cdef("tx$KEY", "var$KEY,8,*");
    $def[0] .= rrd::gradient("tx$KEY", 'ffff42', 'ee7318', "$NAME[$KEY]");
    $def[0] .= rrd::gprint("tx$KEY", array("LAST", "AVERAGE", "MAX"), "\t%4.2lf");
  }
}

?>
