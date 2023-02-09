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
        $stream_id = $in["stream_id"];
        $sql = 'INSERT INTO requests (stream_id, datetime, done) VALUES (' . $stream_id . ',NOW(),NULL);';
        $conn->query($sql);
        $sql = 'SELECT MAX(id) AS id FROM requests;';
        $result = $conn->query($sql);
        while($row = $result->fetch_assoc()) {
            returnInfo($row["id"]);
        }
        // returnInfo();
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
    
    
    function returnInfo($id)
    {
        $retVal = '{"request_id":' . $id . ',';
        $retVal .= '"error":""}';
        sendResultInfoAsJson($retVal);
    }

?>