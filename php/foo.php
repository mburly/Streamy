<?php
    set_time_limit(0);
    ignore_user_abort(1);
    ob_start();
    $configFile = fopen("../streamy.ini", "r") or die("Unable to open file!");
    $host = '';
    $user = '';
    $password = '';
    $client_id = '';
    $secret = '';
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
        else if(strpos($line, "client_id =") !== false)
        {
            $client_id .= rtrim(explode("= ", $line)[1], "\r\n");
        }
        else if(strpos($line, "client_secret =") !== false)
        {
            $secret .= rtrim(explode("= ", $line)[1], "\r\n");
        }
    }
    fclose($configFile);
    $conn = new mysqli($host, $user, $password, $dbname); 
    if($conn->connect_error) {
        returnWithError($conn->connect_error);
    }
    else {
        $name = "forsen";
        $type = "Twitch";
        $url = "twitch.tv/forsen";
        $avatarUrl = '';
        $_POST["avatar_url"] = null;
        if($_POST["avatar_url"] != null) {
            $avatarUrl = $_POST["avatar_url"];
        }
        else {
            if($type == "Twitch") {
                $avatarUrl = getTwitchChannelProfilePicture($client_id, $secret, $name);
                if($avatarUrl == null) {
                    returnWithError("channel does not exist");
                }
            }
        }
        $sql = 'INSERT INTO channels (name, type, url, avatar_url) VALUES ("' . $name . '","' . $type . '","' . $url . '","' . $avatarUrl .  '");';
        $conn->query($sql);
        returnInfo();
    }

    function getTwitchAuth($client_id, $secret) {
        $url = "https://id.twitch.tv/oauth2/token";
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query([
            "client_id" => $client_id,
            "client_secret" => $secret,
            "grant_type" => "client_credentials"
        ]));
        $response = curl_exec($ch);
        curl_close($ch);
        $data = json_decode($response, true);
        return $data["access_token"];
    }

    function getTwitchChannelProfilePicture($client_id, $secret, $name) {
        $url = "https://api.twitch.tv/helix/users?login=" . $name;
        $token = getTwitchAuth($client_id, $secret);
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_HTTPHEADER, [
            "Authorization: Bearer $token",
            "Client-ID: $client_id"
        ]);
        $response = curl_exec($ch);
        curl_close($ch);
        $data = json_decode($response, true);
        if(count($data["data"]) == 0) {
            return null;
        }
        return $data["data"][0]["profile_image_url"];
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