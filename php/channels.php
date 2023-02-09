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
        $sql = 'SELECT name, url, avatar_url, type FROM channels';
        $result = $conn->query($sql);
        $channels = array();
        $urls = array();
        $avatar_urls = array();
        $types = array();
        while($row = $result->fetch_assoc()) {
            array_push($channels, $row["name"]);
            array_push($urls, $row["url"]);
            array_push($avatar_urls, $row["avatar_url"]);
            array_push($types, $row["type"]);
        }
        returnInfo($channels, $urls, $avatar_urls, $types);
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
    
    
    function returnInfo($channels, $urls, $avatar_urls, $types)
    {
        $retVal = '{"channels":[';
        foreach($channels as $channel) {
            $retVal .= '"' . $channel . '",';
        }
        $retVal = substr($retVal, 0, -1);
        $retVal .= '],"urls":[';
        foreach($urls as $url) {
            $retVal .= '"' . $url . '",';
        }
        $retVal = substr($retVal, 0, -1);
        $retVal .= '],"avatar_urls":[';
        foreach($avatar_urls as $avatar_url) {
            $retVal .= '"' . $avatar_url . '",';
        }
        $retVal = substr($retVal, 0, -1);
        $retVal .= '],"types":[';
        foreach($types as $type) {
            $retVal .= '"' . $type . '",';
        }
        $retVal = substr($retVal, 0, -1);
        $retVal .= '],';
        $retVal .= '"error":""}';
        sendResultInfoAsJson($retVal);
    }

?>