var tag = document.createElement('script');
tag.src = "https://youtube.com/iframe_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
var player;



$(document).ready(function () {
    updateItemBoxes();
});




function formatViews(num) {
    return Math.abs(num) > 999 ? Math.sign(num) * ((Math.abs(num) / 1000).toFixed(1)) + 'K' : Math.sign(num) * Math.abs(num)
}
const formatter = new Intl.RelativeTimeFormat(undefined, {
    numeric: 'auto'
})

const DIVISIONS = [
    { amount: 60, name: 'seconds' },
    { amount: 60, name: 'minutes' },
    { amount: 24, name: 'hours' },
    { amount: 7, name: 'days' },
    { amount: 4.34524, name: 'weeks' },
    { amount: 12, name: 'months' },
    { amount: Number.POSITIVE_INFINITY, name: 'years' }
]

function formatTimeAgo(date) {
    let duration = (date - new Date()) / 1000

    for (let i = 0; i <= DIVISIONS.length; i++) {
        const division = DIVISIONS[i]
        if (Math.abs(duration) < division.amount) {
            return formatter.format(Math.round(duration), division.name)
        }
        duration /= division.amount
    }
}

function updateItemBoxes() {
    alert("test")
    $(document).ready(function () {
        const urlParams = new URLSearchParams(window.location.search);
        const queryString = window.location.search;
        console.log($(window).location.pathname)
        if($(window).location.pathname>2){
            queryString += "&format=" + $(window).location.pathname.substring(1)
            console.log(queryString)
        }
        //send get request to flask
        $.get("/tf_map_select_get" + queryString, function (data) {
            var thumbnail_resolution = "0"
            $('#item-boxes-container').empty();
            if (!urlParams.has('showclips')) {
                $.get('/query_yt_clips' + queryString, function (cd) {
                    var clip_container = `<div class="item-clip-container"  id="clip_container_1"></div>`
                    $('#item-boxes-container').append(clip_container);
                    $.each(cd, function (key, clip) {
                        var item_clip = `<div class="item-clip" data-yt_clip_id=${clip['yt_clip_id']} data-yt_video_id=${clip['yt_video_id']} data-yt_clipt=${clip['yt_clipt']} id="${clip['yt_clip_id']}">
                            <div class="item-clip-caption"><span class="item-box-creator">${clip['yt_channel_title']}</span>
                                <span class="item-box-title" title="${clip['yt_clip_title']}">${clip['yt_clip_title']}</span>
                                <div class="item-clip-flag-container">
                                    <span class="item-flag map-flag">${clip['tf_map_full']}</span>
                                    <span class="item-flag type-flag">${clip['tf_resource_type']}</span></div></div></div>`
                        $('#clip_container_1').append(item_clip);
                    });
                    $(".item-clip").click(function () {
                        //on click of preload image, get data-yt_video_id from box and load youtube player
                        var $yt_video_id = $(this).attr('data-yt_video_id');
                        var $yt_clip_id = $(this).attr('data-yt_clip_id');
                        var $yt_clipt = $(this).attr('data-yt_clipt');
                        
                        player = new YT.Player('iframe-holder', {
                            height: '30%',
                            width: '100%',
                            host: 'https://www.youtube.com',
                            videoId: $yt_video_id,
                            playerVars: {
                                'clip': $yt_clip_id,
                                //+`&clipt=`+$yt_clip_data.yt_clipt
                                'clipt': $yt_clipt,
                                'playsinline': 1,
                                'autoplay': 1,
                                'modestbranding': 1,
                                'origin': 'https://mapreview.tf',
                                'rel': 0
                            }
                        });
                    
                        //create jquery-modal
                        $("#video-floating-frame").modal({
                            yt_video_id: $yt_clip_id,
                            fadeDuration: 50,
                            modalClass: "video-floating-frame",
                            showClose: false
                        });



                    });
                });
            }
            //$('#item-boxes-container').append(tst)

            //Iterate over each yt_video object from python and add to boxes-container
            $.each(data, function (key, video) {
                //Define display variables
                const time_ago = formatTimeAgo(Date.parse(video['yt_published_date']))
                const yt_views = formatViews(video['yt_stats_views'])
                const resource_type_display = video['tf_resource_type'];
                const resource_type = video['tf_resource_type'].replace(' ', "_").toLowerCase();
                var tf_map_full = video['tf_map_full'];

                if (tf_map_full == null) {
                    tf_map_full = ""
                };
                var item_box = `<div class="item-box" id=${video['yt_video_id']}><div class="item-box-img"><span class="resource-type-flag" id="${resource_type}">${resource_type_display}</span>
                        <a href="https://youtube.com/channel/${video['yt_channel_id']}"><img class="item-box-logo" src="${video["yt_channel_image"]}"></img></a><div class="item-flag-container"><span class="item-flag map-flag" id="tf_map_flag">${tf_map_full}</span></div>
                        <img class="item-box-img-select" data-yt_video_id=${video['yt_video_id']} src="https://i.ytimg.com/vi/${video['yt_video_id']}/${thumbnail_resolution}.jpg"></img></div>
                        <div class="item-box-caption"><span class="item-box-creator">${video['st_creator_name']}</span><span class="item-box-time">${time_ago}</span><span class="item-box-views">${yt_views} views •</span>
                        <span class="item-box-title" title=${video['yt_video_title']}>${video['yt_video_title']}</span></div></div>`;

                $('#item-boxes-container').append(item_box);

            });

            //Google Ads 
            const g_add = `<div class="item-box" style="height: 212px; width: 300px;><script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-7104910338660789"
                    crossorigin="anonymous"></script>
                    <ins class="adsbygoogle"
                            style="display:block; text-align:center;"
                            data-ad-layout="in-article"
                            data-ad-format="fluid"
                            data-ad-client="ca-pub-7104910338660789"
                            data-ad-slot="3283712263"></ins>
                    <script>
                        (adsbygoogle = window.adsbygoogle || []).push({});
                    </script></div>`
            $('#item-boxes-container').append(g_add);
            $(".item-box-img-select").click(function () {
                //on click of preload image, get data-yt_video_id from box and load youtube player
                var $yt_video_id = $(this).attr('data-yt_video_id');


                
                player = new YT.Player('iframe-holder', {
                    height: '56%',
                    width: '100%',
                    host: 'https://www.youtube-nocookie.com',
                    videoId: $yt_video_id,
                    playerVars: {

                        'playsinline': 1,
                        'autoplay': 1,
                        'modestbranding': 1,
                        'enablejsapi': 1,
                        'origin': 'https://mapreview.tf',
                        'rel': 0
                    },
                    events: {
                        'onReady': onPlayerReady
                    }
                });
            
                //create jquery-modal
                $("#video-floating-frame").modal({
                    yt_video_id: $yt_video_id,
                    fadeDuration: 50,
                    modalClass: "video-floating-frame",
                    showClose: false
                });



            });
        }).fail(function () {
            $('#item-boxes-container').append(`<div>Search Failed</div>`);
            console.log('get fail')
        });

    })
};


$("#video-floating-frame").on({
    'modal:before-block': function (event, modal) {
        //before modal opens
        $yt_video_id = modal.options.yt_video_id
        $.get("/tf_map_select_get?id=" + modal.options.yt_video_id, function (data) {
            $("#ff-title").text(data[$yt_video_id].yt_video_title)
            $("#ff-creator").text(data[$yt_video_id].st_presenter_name)
            $("#ff-views").text(formatViews(data[$yt_video_id].yt_stats_views) + " views")
            $("#ff-age").text(formatTimeAgo(Date.parse(data[$yt_video_id].yt_published_date)))




        })
        //handel chapters
        $("#chapter-container").empty();
        $.get("/lemnoslife_chapter_query?yt_video_id=" + modal.options.yt_video_id, function (data) {
            $.each(data, function (yt_chapter_id, chapter) {
                var _chapter_id = yt_chapter_id
                var _chapter_title = chapter['yt_chapter_title']
                var _chapter_start = chapter['yt_chapter_start']
                $("#chapter-container").append(`<div class="item-flag chapter-flag" id='${_chapter_id}' data-timestart=${_chapter_start}>${_chapter_title}</div>`)
            })
        });


        //change url search parameters once iframe holder is opened
        $prevSearchParams = new URLSearchParams(window.location.search);
        $newSearchParams = new URLSearchParams({ "id": $yt_video_id });
        window.history.replaceState({}, '', `/?` + $newSearchParams.toString());
    },
    'modal:open': function (event, modal) {
        //console.log($(this))
        //$('#iframe-holder').toggleClass('expanded');


    },
    'modal:before-close': function (event, modal) {
        window.history.replaceState({}, '', `/?` + $prevSearchParams.toString());
        player.destroy();
        //console.log("ytplayer destroyed: " + $yt_video_id)
    }
});


function onPlayerReady(event) {

    event.target.playVideo();
    var toggled = true;
    if (event = YT.PlayerState.PLAYING && toggled) {
        var toggled = false;
        console.log("playing")
        $('#iframe-holder').toggleClass('video-iframe');
    }

}

//Seek to timestamp data contained in button
$('.chapter-container').on('click', "div.chapter-flag", function () {
    YT.get('iframe-holder').seekTo($(this).attr('data-timestart'), true);
});