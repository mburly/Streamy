<?php
    set_time_limit(0);
    ignore_user_abort(1);
    ob_start();
    $in = getRequestInfo();

    $conn = new mysqli("localhost", "root", "", "streamy"); 
    if($conn->connect_error) {
        returnWithError($conn->connect_error);
    }
    else {
        $name = $in["name"];
        $sql = 'SELECT id FROM channels WHERE name = "' . $name .  '";';
        $channel_id = $conn->query($sql)->fetch_assoc()["id"];
        $sql = 'DELETE FROM channels WHERE name = "' . $name . '";';
        $conn->query($sql);
        $sql = 'DELETE FROM streams WHERE channel_id=' . $channel_id . ';';
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