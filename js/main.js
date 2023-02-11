var _active = false;
var _state = '';
var _oldNames = []
var _removeChannels = []

loadStreams()
setInterval(function() {
    loadStreams();
},3000);


var removeListener = function() {
    if(this.style.backgroundColor === "" || this.style.backgroundColor === "white") {
        this.style.backgroundColor = "#c6c6c6";
        var index = _removeChannels.indexOf(this.id);
        if (index == -1) {
            _removeChannels.push(this.id);
        }
        console.log(_removeChannels);
    } 
    else {
        this.style.backgroundColor = "white";
        var index = _removeChannels.indexOf(this.id);
        if (index !== -1) {
            _removeChannels.splice(index, 1);
        }
        console.log(_removeChannels);
    }
  };

$('body').on('click', '.panel-block', function() {
    var id = $(this).attr('id');
    var currentElement = document.getElementById(id);
    var hasInputChild = [...currentElement.children].some(child => child.tagName === 'INPUT');
    if (hasInputChild || _state == 'remove' || _active == true) {
        return;
    }
    var id = $(this).attr('id').split('-');
    var stream_id = id[1];
    $.post("php/request.php", {stream_id: stream_id});
    var toast = document.getElementById("snackbar");
    toast.className = "show";
    setTimeout(function(){ toast.className = toast.className.replace("show", ""); }, 3000);
    _active = true;
});

$('body').on('click', '#addChannelButtonSubmit', function() {
    var url = $('#channelUrlInput')[0].value;
    if(url == '') {
    }
    else {
        if(url.split('youtube.com/@').length > 1) {
            // youtube url
            var channel_name = url.split('@')[1];
            $.post("php/addChannel.php", {name: channel_name, url: url, avatar_url: null, type: "Youtube"})
            .done(function(data) {
            });
            var toast = document.getElementById("snackbar");
            toast.className = "show";
            setTimeout(function(){ toast.className = toast.className.replace("show", ""); }, 3000);
            hide('addChannelCard');
        }
        else if(url.split('twitch.tv/').length > 1) {
            // twitch url
            var channel_name = url.split('/')[1];
            $.post("php/addChannel.php", {name: channel_name, url: url, avatar_url: null, type: "Twitch"})
            .done(function(data) {
            });
            var toast = document.getElementById("snackbar");
            toast.className = "show";
            setTimeout(function(){ toast.className = toast.className.replace("show", ""); }, 3000);
            hide('addChannelCard');
        }
        else {
            // display error
            show('badChannelMessage');
        }
        document.getElementById("channelUrlInput").value = '';
    }
});

$('body').on('click', '#forceCloseButton', function() {
    var toast = document.getElementById("snackbar");
    toast.className = "show";
    setTimeout(function(){ toast.className = toast.className.replace("show", ""); }, 3000);
    $.get("php/updateLastRequest.php", function() {
    });
    _active = false;
});

$('body').on('click', '#addChannelButton', function() {
    show('addChannelCard');
});

$('body').on('click', '#closeAddChannelButton', function() {
    hide('addChannelCard');
});

$('body').on('click', '#refreshButton', function() {
    window.location.reload();
});

$('body').on('click', '#editChannelsButton', function() {
    var editButton = document.getElementById("editChannelsButton");
    var doneButton = document.createElement("span");
    doneButton.className = "button is-success";
    doneButton.id = "editChannelsDoneButton";
    doneButton.innerHTML = "Done";
    editButton.parentNode.replaceChild(doneButton, editButton);
    var spans = document.querySelectorAll('.channel-name');
    spans.forEach(span => {
        var input = document.createElement('input');
        _oldNames.push(span.textContent);
        input.value = span.textContent;
        input.className = "channel-name channel-name-input";
        input.id = span.id;
        span.replaceWith(input);
    });
});

$('body').on('click', '#editChannelsDoneButton', function() {
    var inputs = document.querySelectorAll('.channel-name');
    var counter = 0;
    inputs.forEach(input => {
        const span = document.createElement('span');
        if(input.value != _oldNames[counter]) {
            if(input.value == '' || input.value == ' ') {
                
            }
            else {
                span.textContent = input.value;
                $.post("php/updateDisplayName.php", {channel: input.id, display_name: input.value});
            }
        }
        else {
            span.textContent = _oldNames[counter];
        }
        span.textContent = input.value;
        span.className = "channel-name";
        span.id = input.id;
        input.replaceWith(span);
        counter += 1;
    });
    var doneButton = document.getElementById("editChannelsDoneButton");
    var editButton = document.createElement("span");
    editButton.className = "button is-dark";
    editButton.id = "editChannelsButton";
    editButton.innerHTML = "Edit";
    doneButton.parentNode.replaceChild(editButton, doneButton);
});

$('body').on('click', '#removeChannelsButton', function() {
    var originalButton = document.getElementById("removeChannelsButton");
    var doneButton = document.createElement("span");
    doneButton.innerHTML = "Done";
    doneButton.setAttribute("class", "button is-danger");
    doneButton.setAttribute("id", "removeChannelsDonebutton");
    originalButton.parentNode.replaceChild(doneButton, originalButton);
    var panelBlocks = document.getElementsByClassName("panel-block");
    for (var i = 0; i < panelBlocks.length; i++) {
        panelBlocks[i].addEventListener("click", removeListener);
    }
    _state = "remove";
});

$('body').on('click', '#removeChannelsDonebutton', function() {
    var panelBlocks = document.getElementsByClassName("panel-block");
    for (var i = 0; i < panelBlocks.length; i++) {
        panelBlocks[i].removeEventListener("click", removeListener);
        panelBlocks[i].style.backgroundColor = "white";
    }

    for(let i = 0; i < _removeChannels.length; i++) {
        var name = _removeChannels[i].split('-')[0];
        $.post("php/deleteChannel.php", {name: name});
    }

    var doneButton = document.getElementById("removeChannelsDonebutton");
    var removeButton = document.createElement("span");
    removeButton.className = "button is-danger";
    removeButton.id = "removeChannelsButton";
    removeButton.innerHTML = "Remove";
    if (doneButton) {
        doneButton.parentNode.replaceChild(removeButton, doneButton);
    }

    _removeChannels = [];
    _state = "";
});

function loadStreams() {
    $.get("php/streams.php", function(data, status) {
        var data = JSON.parse(data);
        if(data["error"] == "1") {
            var ids = getStreamIdsOnScreen();
            for(let i = 0; i < ids.length; i++) {
                remove(ids[i]);
            }
            return;
        }
        var streamsOnScreen = getStreamsOnScreen();
        var active_streams = [];
        for(let i = 0; i < data["channels"].length; i++) {
            var stream_id = data["stream_ids"][i];
            var channel = data["channels"][i];
            var name = data["channels"][i];
            var type = data["types"][i];
            var avatar_url = data["avatar_urls"][i];
            var panel_id = channel + '-' + stream_id + '-panelBlock';
            if(data["display_names"][i] != "") {
                name = data["display_names"][i];
            }
            if(avatar_url == "") {
                avatar_url = "images/user.svg";
            }
            if(type == "Youtube") {
                if(!elementExists(panel_id)) {
                    $('#streamsPanel').append('<a class="panel-block" id="' + channel + '-' + + stream_id + '-panelBlock"><span class="channel-icon"><img src="' + avatar_url + '" class="channel-image"></span><span class="channel-name" id="' + channel + '">' + name + '</span><span class="channel-info-title-text"></span><span class="channel-source source-youtube"><span class="channel-view-count"></span><i class="fab fa-youtube channel-source-icon"></i></span></a>');
                }
            }
            else {
                if(!elementExists(panel_id)) {
                    $('#streamsPanel').append('<a class="panel-block" id="' + channel + '-' + + stream_id + '-panelBlock"><span class="channel-icon"><img src="' + avatar_url + '" class="channel-image"></span><span class="channel-name" id="' + channel + '">' + name + '</span><span class="channel-info-title-text"></span><span class="channel-source source-twitch"><span class="channel-view-count"></span><i class="fab fa-twitch channel-source-icon"></i></span></a>');
                }
            }
            active_streams.push(panel_id);
        }
        for(let i = 0; i < streamsOnScreen.length; i++) {
            if(!active_streams.includes(streamsOnScreen[i])) {
                remove(streamsOnScreen[i]);
            }
        }
    });
}

function getStreamsOnScreen() {
    var ele = document.getElementById('streamsPanel');
    var channels = [];
    for (var child of ele.children) {
        if(child.tagName == 'A') {
            channels.push(child.id);
        }
    }
    return channels;
}

function getStreamIdsOnScreen() {
    var ele = document.getElementById('streamsPanel');
    var ids = [];
    for (var child of ele.children) {
        if(child.tagName == 'A') {
            ids.push(child.id);
        }
    }
    return ids;
}

function getStreamId(channel) {
    var ele = document.getElementById('streamsPanel');
    var id = '';
    for (var child of ele.children) {
        if(child.tagName == 'A') {
            var id = child.id.split('-')
            if(id[0] == channel) {
                return id[1];
            }
        }
    }
    return id;
}

function elementExists(id) {
    var element =  document.getElementById(id);
    if (typeof(element) != 'undefined' && element != null)
    {
        return true;
    }
    return false;
}

function hide(id) {
    $('#' + id).css("display", "none");
}

function remove(id) {
	try {
		document.getElementById(id).remove();
	}
	catch(err) {
		console.log(err);
	}
}

function show(id) {
    $('#' + id).css("display", "block");
}