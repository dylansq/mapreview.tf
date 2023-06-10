//Youtube iFrame API
var tag = document.createElement('script');
tag.src = "https://youtube.com/iframe_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);



//Run box upadateItemBoxes when page is loaded
$(document).ready(function () {
    window.onYouTubeIframeAPIReady = function() {
        var yt_player;
    updateItemBoxes();}
});

//add ytplayer


function updateItemBoxes() {

        const urlParams = new URLSearchParams(window.location.search);
        var queryString = window.location.search;
        const qs_len = queryString.length
        if(window.location.pathname.length>2){
            var qamp
            if(qs_len==0){qamp = "?"}else{qamp = "&"}
            queryString = queryString + qamp + "format=" + window.location.pathname.substring(1)
        }
        //GET request to Flask with current query string
        $.get("/tf_map_select_get" + queryString, function (data) {
            data = JSON.parse(data)
            //Remove previous container contents
            $('#item-boxes-container').empty();
            //Iterate over each yt_video object from Flask and add to boxes-container

            //Update selectize
            

            jQuery.each(data.counts.tf_resource_type, function(i, val) {
                $('#type')[0].selectize.addOption(val);
                $('#type')[0].selectize.updateOption(val.value,val)
                updateSelectedParms('type')
            });

            jQuery.each(Object.keys($('#type')[0].selectize.options).filter(x => !Object.keys(data.counts.tf_resource_type).map((key) => [data.counts.tf_resource_type[key].value][0]).includes(x)), function(i, val) {
                $('#type')[0].selectize.removeOption(val)
            });

            // existing options: Object.keys($('#map')[0].selectize.options)
            jQuery.each(data.counts.tf_map_full, function(i, val) {
                $('#map')[0].selectize.addOption(val);
                $('#map')[0].selectize.updateOption(val.value,val)
                //add    Object.keys(data.counts.tf_map_full).map((key) => [data.counts.tf_map_full[key].value][0])
                updateSelectedParms('map')
            });

            //Results from flask Object.keys(data.counts.tf_map_full).map((key) => [data.counts.tf_map_full[key].value][0])
            //Objects in search Object.keys($('#map')[0].selectize.options)
            
            jQuery.each(Object.keys($('#map')[0].selectize.options).filter(x => !Object.keys(data.counts.tf_map_full).map((key) => [data.counts.tf_map_full[key].value][0]).includes(x)), function(i, val) {
                $('#map')[0].selectize.removeOption(val)
            });

            jQuery.each(data.counts.tf_class, function(i, val) {
                $('#class')[0].selectize.addOption(val);
                $('#class')[0].selectize.updateOption(val.value,val)
                updateSelectedParms('class')
            });
            try{
            jQuery.each(data.counts.tf_role, function(i, val) {
                $('#role')[0].selectize.addOption(val);
                $('#role')[0].selectize.updateOption(val.value,val)
                updateSelectedParms('role')
            });
        }catch{

        }
            jQuery.each(data.counts.tf_match_format, function(i, val) {
                $('#format')[0].selectize.addOption(val);
                $('#format')[0].selectize.updateOption(val.value,val)
                updateSelectedParms('format')
                if(window.location.pathname.length >2){
                    console.log('changing format' + window.location.pathname.substring(1) )
                    $('#format')[0].selectize.setValue(window.location.pathname.substring(1));
                }
            });
            

            $.each(data.results, function (key, video) {
                //Define display variables 
                const thumbnail_resolution = "0"

                var datestr = video['yt_published_date'].split(/[^0-9]/);
                var pubdate = new Date (datestr[0],datestr[1]-1,datestr[2],datestr[3],datestr[4],datestr[5] );
                var time_ago = formatTimeAgo(pubdate);

                const yt_views = formatViews(video['yt_stats_views']);
                const resource_type_display = video['tf_resource_type'];
                const resource_type = video['tf_resource_type'].replace(' ', "_").toLowerCase();
                var tf_map_full = video['tf_map_full'];
                var tf_map_flag
                if ((tf_map_full != null) && (tf_map_full != 'none')) {tf_map_flag = `<span class='item-flag map-flag'">${tf_map_full}</span>`} else { tf_map_flag = ``}
                var display_name
                if (video['mrtf_display_name'] != null) {display_name = video['mrtf_display_name']} else {display_name = video['yt_channel_title']}
                var tf_class_flag
                var tf_class= video['relevant_classes']
                if (video['relevant_classes'] != null) {tf_class_flag = `<span class='item-flag class-flag'">${tf_class}</span>`} else { tf_class_flag = ``}
                var yt_video_new = (new Date() - Date.parse(video['yt_published_date']) ) / 1000 /(60*60*24)
                
                var yt_video_new_flag = ''
                if (yt_video_new <= 120) {
                    yt_video_new_flag = `<svg class='new-flag' xmlns="http://www.w3.org/2000/svg" width="30" height="30" viewBox="0 0 1012 1030">
                    <defs><style> .cls-1 {fill: #ef9849;} .cls-1, .cls-2 {fill-rule: evenodd;} </style></defs>
                    <path class="cls-1" d="M4,379l137-67L124,169l150,5L330,30l129,76L571,3l84,127L796,94l14,150,148,35L901,420l108,96L895,612l51,138L804,789,786,931,637,895l-84,122L448,921,312,982,262,841l-147-1,20-147L9,625,94,505Z"/>
                    <path class="cls-2" d="M274.388,604.066l39.551-3.076-3.223-204.053-48.34,1.9,6.3,131.4-93.6-133.594H132.445V606.7h56.4l-2.929-127.149ZM505.535,447.035v-50.1H335.466L338.1,606.7,488.4,604.066l-1.172-39.99-95.068,3.076L391.57,544.3h62.988V516.175H390.4l-0.879-69.14H505.535Zm167.412-56.194-30.908-2.49L603.074,514.767,574.8,388.351l-58.154,6.885L566.16,599h51.562l43.8-124.219,30.615,116.748,46.582,5.127,53.028-197.461-49.512-8.936L707.517,528.244Zm186.136,10.637-42.48-2.051-5.42,136.231,35.6,2.051ZM802.76,593.519a22.738,22.738,0,0,0,5.567,6.812,26.571,26.571,0,0,0,7.763,4.467,25.132,25.132,0,0,0,8.863,1.612,26.773,26.773,0,0,0,16.919-6.079,22.811,22.811,0,0,0,5.566-6.812,21.084,21.084,0,0,0,2.417-8.789,24.029,24.029,0,0,0-1.318-8.569,21.982,21.982,0,0,0-4.688-7.837,24.749,24.749,0,0,0-7.983-5.713,24.381,24.381,0,0,0-10.913-2.051,24.623,24.623,0,0,0-17.8,7.764,24.4,24.4,0,0,0-6.519,16.406A18.277,18.277,0,0,0,802.76,593.519Z"/></svg>`
                }
                var item_box = `<div class='item-box' id=${video['yt_video_id']}>${yt_video_new_flag}<div class="item-wrap"><div class="item-box-img"><span class="resource-type-flag" id="${resource_type}">${resource_type_display}</span>
                        <a href="https://youtube.com/channel/${video['yt_channel_id']}"><img class="item-box-logo logo-absolute" src="${video["yt_channel_image"]}"></img></a><div class="item-flag-container">${tf_class_flag}${tf_map_flag}</div>
                        <img class="item-box-img-select" data-yt_video_id=${video['yt_video_id']} src="https://i.ytimg.com/vi/${video['yt_video_id']}/${thumbnail_resolution}.jpg" loading="lazy"></img></div>
                        <div class="item-box-caption"><div class="caption-top"><span class="item-box-creator">${display_name}</span><span class="item-box-views">${yt_views} views •</span><span class="item-box-time">${time_ago}</span></div>
                        <span class="item-box-title" title=${video['yt_video_title']}>${video['yt_video_title']}</span></div></div></div>`;

                $('#item-boxes-container').append(item_box);

            });



        }).done(function(){
            //Handel fetching and displaying clips
            if (!urlParams.has('showclips')) {
                $.get('/query_yt_clips' + queryString, function (cd) {
                    var container_i = 0;
                    var clip_i = 0;
                    var clip_container = `<div class="item-clip-container"  id="clip_container_${container_i}"></div>`
                    
                    $('#item-boxes-container').append(clip_container);
                    $.each(cd, function (key, clip) {
                        
                        if (clip_i % 4 == 0){
                            container_i +=1;
                            clip_container = `<div class="item-clip-container"  id="clip_container_${container_i}"></div>`
                            $('#item-boxes-container').append(clip_container);
                        }

                        var item_clip = `<div class="item-clip" data-yt_clip_id=${clip['yt_clip_id']} data-yt_video_id=${clip['yt_video_id']} data-yt_clipt=${clip['yt_clipt']} id="${clip['yt_clip_id']}">
                            <div class="item-clip-caption"><span class="item-box-creator">${clip['yt_channel_title']}</span>
                                <span class="item-box-title" title="${clip['yt_clip_title']}">${clip['yt_clip_title']}</span>
                                <div class="item-clip-flag-container">
                                    <span class="item-flag map-flag">${clip['tf_map_full']}</span>
                                    <span class="item-flag type-flag">${clip['tf_resource_type']}</span></div></div></div>`
    
                        $(`#clip_container_${container_i}`).append(item_clip);
                        clip_i +=1;
                    });
            
                });
            }
        }).fail(function () {
            //GET Request to Flask Failed
            $('#item-boxes-container').append(`<div>Search Failed</div>`);
            console.log('get fail')
        });

};

$(".item-boxes-container").on('click', "img.item-box-img-select", function () {
    //on click of preload image, get data-yt_video_id from box and load youtube player
    var $yt_video_id = $(this).attr('data-yt_video_id');

    //create jquery-modal
    $("#video-floating-frame").modal({
        yt_video_id: $yt_video_id,
        fadeDuration: 50,
        modalClass: "video-floating-frame",
        showClose: false
    });



});


$(".item-boxes-container").on('click', "div.item-clip", function () {
    //on click of preload image, get data-yt_video_id from box and load youtube player
    var $yt_video_id = $(this).attr('data-yt_video_id');
    var $yt_clip_id = $(this).attr('data-yt_clip_id');
    var $yt_clipt = $(this).attr('data-yt_clipt');
    //create jquery-modal
    $("#video-floating-frame").modal({
        yt_video_id: $yt_video_id,
        yt_clip_id: $yt_clip_id,
        yt_clipt: $yt_clipt,
        fadeDuration: 50,
        modalClass: "video-floating-frame",
        showClose: false
    });



});
var prevPath;
$("#video-floating-frame").on({
    'modal:before-block': function (event, modal) {
        //before modal opens
        var yt_video_id = modal.options.yt_video_id
        $.get("/tf_map_select_get?id=" + modal.options.yt_video_id, function (video) {
            video = JSON.parse(video)['results'][0]
            $("#ff-title").text(video.yt_video_title)
            $("#ff-creator").text(video.st_presenter_name)
            $("#ff-views").text(formatViews(video.yt_stats_views) + " views")
            $("#ff-logo-link").attr("href","https://youtube.com/channel/"+video.yt_channel_id)
            $("#ff-logo-img").attr("src",video.yt_channel_image)
            $("#ff-age").text(formatTimeAgo(Date.parse(video.yt_published_date)))

        })
        //handel chapters
        $("#chapter-container").empty();
        $.get("/get_chapters?yt_video_id=" + modal.options.yt_video_id, function (data) {
            $.each(data, function (yt_chapter_id, chapter) {
                var _chapter_id = yt_chapter_id
                var _chapter_title = chapter['yt_chapter_title']
                var _chapter_start = chapter['yt_chapter_start']
                $("#chapter-container").append(`<div class="item-flag chapter-flag" id='${_chapter_id}' data-timestart=${_chapter_start}>${_chapter_title}</div>`)
            })
        });
        //change url search parameters once iframe holder is opened
        $prevSearchParams = new URLSearchParams(window.location.search);
        $newSearchParams = new URLSearchParams({ "id": yt_video_id });
        prevPath = window.location.pathname;
        window.history.replaceState({}, '', prevPath + `?` + $newSearchParams.toString());
    },
    'modal:open': function(event,modal){
        var yt_video_id = modal.options.yt_video_id
        var yt_clip_id = modal.options.yt_clip_id
        var yt_clipt = modal.options.yt_clipt
        yt_player = new YT.Player('iframe-holder', {
            height: '30%',
            width: '100%',
            host: 'https://www.youtube.com',
            videoId: yt_video_id,
            playerVars: {'clip': yt_clip_id,'clipt': yt_clipt,'playsinline': 1,'autoplay': 1,'modestbranding': 1,'origin': location.href,'widget_referrer' : location.href, 'enablejsapi': 0,'rel': 0}
            //,events: {'onReady': onPlayerReady}
        });
    },
    'modal:before-close': function (event, modal) {

        if(Array.from($prevSearchParams).length == 0){
            window.history.replaceState({}, '', prevPath);
        }else{
            window.history.replaceState({}, '', prevPath+`?`+$prevSearchParams.toString());
    }

        yt_player.destroy();
    }
});

function loadVideo(yt_video_id,clip=null,clipt=null){
    if (clip == null){var clip_string = ``}else{var clip_string = `?clip=${clip}&clipt=${clipt}`}
    console.log(`http://www.youtube.com/clip/${yt_video_id}${clip_string}`)
    YT.get('iframe-holder').loadVideoByUrl({'mediaContentUrl':`http://www.youtube-nocookie.com/embed/${yt_video_id}${clip_string}`})
}

function onPlayerReady(event) {
    if($.modal.isActive()){
        var m = $.modal.getCurrent().options;
        loadVideo(m.yt_video_id,m.yt_clip_id,m.yt_clipt)
        console.log($.modal.getCurrent().options.yt_video_id)
    }


}

//Seek to timestamp data contained in button
$('.chapter-container').on('click', "div.chapter-flag", function () {
    YT.get('iframe-holder').seekTo($(this).attr('data-timestart'), true);
});


//Text formatting functions
function formatViews(num) {
    return Math.abs(num) > 999 ? Math.sign(num) * ((Math.abs(num) / 1000).toFixed(0)) + 'K' : Math.sign(num) * Math.abs(num)
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

$('.alert-container').click(function(){
    $('.alert-container').hide();
})


