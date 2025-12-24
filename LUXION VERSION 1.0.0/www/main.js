$(document).ready(function() {
    $('.text').textillate({
        loop: true,
        sync: true,
        in: {
            effect: "bounceIn",
        },
        out: {
            effect: "bounceOut",
        },
    });

    var siriWave = new SiriWave({
        container: document.getElementById("siri-container"),
        width: 800,
        height: 200,
        style: "ios9",
        amplitude: "1",
        speed: "0.30",
        autostart: true
    });

    $('.siri-message').textillate({
        loop: true,
        sync: true,
        in: {
            effect: "fadeInUp",
            sync: true,
        },
        out: {
            effect: "fadeOutUp",
            sync: true,
        },
    });

    $("#MicBtn").click(function() {
        $("#Oval").attr("hidden", true);
        $("#SiriWave").attr("hidden", false);
        eel.playClickSound();
        eel.allCommands()();

        $(this).addClass('active');
    });

    $("#devBtn").click(function(e) {
        e.preventDefault();
        e.stopPropagation();

        $(this).addClass('active');
        

        showDeveloperInfo();
        

        setTimeout(() => {
            $(this).removeClass('active');
        }, 1000);
    });


    function showDeveloperInfo() {

        if ($(".dev-info-panel").length) {
            $(".dev-info-panel").remove();
            return;
        }

        const devPanel = $(`
            <div class="dev-info-panel">
                <div class="dev-header">
                    <h5><i class="bi bi-robot"></i>Luxion</h5>
                    <button class="close-dev-info"><i class="bi bi-x-lg"></i></button>
                </div>
                <div class="dev-content">
                    <p><i class="bi bi-person-circle"></i> <strong>Developer:</strong> Tej</p>
                    <p><i class="bi bi-tags"></i> <strong>Version:</strong> 1.0.0</p>
                    <p><i class="bi bi-cpu"></i> <strong>Status:</strong> Active</p>
                    <hr>
                    <p class="dev-note"><i class="bi bi-info-circle"></i> Hi everyone</p>
                </div>
            </div>
        `);

        $("body").append(devPanel);
        
        $(".close-dev-info").click(function() {
            $(".dev-info-panel").remove();
        });
        

        setTimeout(() => {
            $(".dev-info-panel").remove();
        }, 10000);
    }

    $(document).click(function(e) {
        if (!$(e.target).closest('.dev-btn, .dev-info-panel').length) {
            $(".dev-info-panel").remove();
        }
    });
});