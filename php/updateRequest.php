<?php
    set_time_limit(0);
    ignore_user_abort(1);
    ob_start();
    $in = getRequestInfo();
    $configFile = fopen("../streamy.ini", "r") or die("Unable to open file!");
    $host = '';
    $user = '';
    $password = '';
    $dbname = 'streamy';
    while(!feof($configFile)) {
        $line = fgets($configFile);
        if(strpos($line, "host =") !== false)
        {
            $host .= rtrim(explode("= ", $line)[1], "\r\n");
        }
        else if(strpos($line, "user =") !== false)
        {
            $user .= rtrim(explode("= ", $line)[1], "\r\n");
        }
        else if(strpos($line, "password =") !== false)
        {
            $password .= rtrim(explode("= ", $line)[1], "\r\n");
        }
    }
    fclose($configFile);

    $conn = new mysqli($host, $user, $password, $dbname); 
    if($conn->connect_error) {
        returnWithError($conn->connect_error);
    }
    else {
        $request_id = $in["request_id"];
        $sql = 'UPDATE requests SET done = 1 WHERE id = ' . $request_id . ';';
        $conn->query($sql);
        returnInfo();
    }

    function getRequestInfo()
    {
        return json_decode(file_get_contents('php://input'), true);
    }

    function sendResultInfoAsJson( $obj )
    {
        header('Content-Type: text/html');
        echo $obj;
    }

    function returnWithError( $err )
    {
        $retValue = '{"id":0,"error":"' . $err . '"}';
        sendResultInfoAsJson( $retValue );
    }
    
    
    function returnInfo()
    {
        $retVal = '{';
        $retVal .= '"error":""}';
        sendResultInfoAsJson($retVal);
    }

?>