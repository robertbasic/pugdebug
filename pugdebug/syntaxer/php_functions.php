<?php

$functions = get_defined_functions();

if (isset($functions['internal'])) {
    $functions = $functions['internal'];

    $functions = json_encode($functions);

    echo $functions;
}
