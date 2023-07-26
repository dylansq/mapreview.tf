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
        $.get("/tf_map_select_get/" + queryString, function (data) {
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
        $.get("/tf_map_select_get?id=" + modal.options.yt_video_id, function (data) {
            data = JSON.parse(data)
            video = data['results'][0]
            $("#ff-title").text(video.yt_video_title)

            if (video.mrtf_display_name != null) {display_name = video.mrtf_display_name} else {display_name = video.yt_channel_title}
            $("#ff-creator").text(display_name)
            $("#ff-views").text(formatViews(video.yt_stats_views) + " views")
            $("#ff-logo-link").attr("href","https://youtube.com/channel/"+video.yt_channel_id)
            $("#ff-logo-img").attr("src",video.yt_channel_image)
            $("#ff-age").text(formatTimeAgo(Date.parse(video.yt_published_date)))
            $('#tag-submit-dialogue').empty();
            
            votes = data['votes']
            tags = data['tags']
            common_tags = data['common_tags']

            
            $('.frag-button').removeClass("frag-selected")
            $(`span[data-frag="${votes['user']}"]`).toggleClass("frag-selected")
            $('.frag-up').text('+'+votes['up'])
            $('.frag-down').text('-'+votes['down'])

            $('.tag-container-display').empty();
            $('.tag-submit-dialogue').empty();
            
            var tag_items = ``
            if($.isEmptyObject(tags)){
                $('.tag-opener').text(`+ Add Tag`)
                $('.tag-opener').css("font-size", '10px');
            }else{
                $('.tag-opener').text(`+`)
                $('.tag-opener').css("font-size", '20px');
            }
            $.each(tags,function(tag,counts){
                console.log([tag, counts['count'], counts['user']])
                tag_select_class = ``
                if(counts['user']){tag_select_class = `tag-selected`}
                tag_items += `<div class="tag-button item-flag ${tag_select_class}" data-tag="${tag}">${tag} <span class="tag-count">x ${counts['count']}</span></div>`
                common_tags.splice( $.inArray(tag, common_tags), 1 );
                
            })
            

            console.log(common_tags)
            $('.tag-container-display').append(tag_items);

            $.each(common_tags,function(i,tag){
                $('.tag-submit-dialogue').append(`<div class="tag-button item-flag tag-submit-dialogue-button" data-tag="${tag}">${tag}</div>`)
            });


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

        //handel votes
        
        //$.get("/get_user_vote?mrtf_item_id=" + modal.options.yt_video_id, function (data) {
        //    console.log(data)
        //});
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


$('.frag-button').on('click',function(e){
    var $fragbutton = $(this)
    $.post('/submit_vote',{vote:e.target.dataset.frag},function(data){
        console.log(data['tags'])
        $('.frag-button').not($fragbutton).removeClass("frag-selected")
        $fragbutton.toggleClass("frag-selected")
        $('.frag-up').text('+'+data['votes']['up'])
        $('.frag-down').text('-'+data['votes']['down'])



    }).fail(function(data) {
        alert(data.responseText)
      })
})




$('.tag-container').on('click','.tag-button',function(e){
    var $tagbutton = $(this)
    $.post('/submit_tag',{tag:e.target.dataset.tag},function(data){
        $tagbutton.toggleClass("tag-selected")
        if($('.tag-submit-dialogue').is($tagbutton.parent())){
            var $tagmove = $tagbutton.detach();
            $tagmove.removeClass('tag-submit-dialogue-button')
            $('.tag-container-display').append($tagmove)
        }
    }).fail(function(data) {
        alert(data.responseText)
      })
})


$('.tag-opener').on('click',function(){
    if($('.tag-submit-dialogue').is(':visible')){
        $('.tag-submit-dialogue').hide();
    }else{
        $('.tag-submit-dialogue').show();
    }
})

$(document).mouseup(function(e){
    if (!$('.tag-submit-dialogue').is(e.target) || !$('.tag-opener').is(e.target)){
        $('.tag-submit-dialogue').hide();
    }
});