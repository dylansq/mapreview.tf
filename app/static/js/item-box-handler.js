//Youtube iFrame API
var tag = document.createElement('script');
tag.src = "https://youtube.com/iframe_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

//Run box initItemBoxes when page is loaded
window.onYouTubeIframeAPIReady = function() {
$(document).ready(function () {
    console.log('documnt ready')
    
        var yt_player;
        console.log('loading yt iframe api')
        initItemBoxes();
});}

function initItemBoxes(){
/**
 * Creates initial get request to server for all items and creates Isotope functions 
 * TODO:// make dictionary returning {}
 */

    //Get current URL Search parameters to reference later
    console.log('before init get')
    const urlParams = new URLSearchParams(window.location.search);
    var queryString = window.location.search;

    //GET request to API with current query string
    $.get("/tf_map_select_get", function (data) {
        console.log('init get')
        data = JSON.parse(data)
        //Remove previous container contents
        $('#item-boxes-container').empty();

        //$('#item-boxes-container').append(`<div class="grid-sizer"></div><div class="gutter-sizer"></div>`)

        //Iterate over each listing
        $.each(data.results, function (key, video) {
            console.log('looping items')
            //Define display variables 
            const thumbnail_resolution = "0"

            var filter_string = ``
            var time_ago_string = ``
            var yt_views_string = ``
            
            //Youtube Stats
            var date_arr = video['yt_published_date'].split(/[^0-9]/);
            var published_date = new Date (date_arr[0],date_arr[1]-1,date_arr[2],date_arr[3],date_arr[4],date_arr[5]);
            var published_age = formatTimeAgo(published_date)
            time_ago_string += `<span class="item-box-time">${published_age}</span>`
            yt_views_string  += `<span class="item-box-views">${formatViews(video['yt_stats_views'])} views •</span>`
            
            //Resource Type
            var resource_type_flag_string = ``
            resource_type_flag_string += `<span class="resource-type-flag" id="${video['tf_resource_type'].replace(' ', "_").toLowerCase()}">${video['tf_resource_type']}</span>`
            filter_string += `type-${video['tf_resource_type'].replace(' ', "+")},`

            //Map
            var tf_map_flag_string = ``
            if ((video['tf_map_full'] != null) && (video['tf_map_full'] != 'none')) {
                tf_map_flag_string += `<span class='item-flag map-flag'">${video['tf_map_full']}</span>`
                filter_string += `map-${video['tf_map_full']},`
            }

            //Display Name
            var display_name = ``
            if (video['mrtf_display_name'] != null) {
                display_name = video['mrtf_display_name']
                filter_string += `creator-${video['mrtf_display_name']},`
            } else {
                display_name = video['yt_channel_title']
                filter_string += `creator-${video['yt_channel_title']},`
            }

            //Classes
            var tf_class_flag_string = ``
            var tf_class = video['relevant_classes']
            if (video['relevant_classes'] != null) {
                tf_class_flag_string += `<span class='item-flag class-flag'">${tf_class}</span>`
                filter_string += `class-${tf_class},`
            }
            if (video['tf_match_format'] == 'sixes') {
                if (video['tf_role_combo'] != null){filter_string += `role-combo,`}
                if (video['tf_role_flank'] != null){filter_string += `role-flank,`}
                if (video['tf_role_offclass'] != null){filter_string += `role-offclass,`}
            }
            
            if (video['mrtf_language'] != null) {
                filter_string += `language-${video['mrtf_language']},`
            }
            
            if (video['tf_match_format'] != null) {
                filter_string += `gamemode-${video['tf_match_format']},`
            }
            mrtf_votes_sum_flag_string = ``
            try{
                if(video['mrtf_votes_sum'] != null){
                    if(video['mrtf_votes_sum'] > 0){
                        mrtf_votes_sum_flag_string += `<span class="item-flag frag-flag-up">+${video['mrtf_votes_sum']}<span class="frag-flag-hover"> Frags</span></span>`
                    }else if(video['mrtf_votes_sum'] < 0){
                        mrtf_votes_sum_flag_string +=  `<span class="item-flag frag-flag-down">${video['mrtf_votes_sum']}<span class="frag-flag-hover"> Frags</span></span>`
                    }
                }
            }catch{
                console.log('error logging votes for ', video[yt_video_id])
            }
            //New
            var yt_video_new_flag = ``
            var yt_video_days_old = (new Date() - Date.parse(video['yt_published_date']) ) / 1000 /(60*60*24)
            filter_string += `age-${Math.floor(yt_video_days_old)},`
            if (yt_video_days_old <= 120) {
                //If age is <= 120 days, show new tag
                yt_video_new_flag = `<svg class='new-flag' xmlns="http://www.w3.org/2000/svg" width="30" height="30" viewBox="0 0 1012 1030">
                <defs><style> .cls-1 {fill: #ef9849;} .cls-1, .cls-2 {fill-rule: evenodd;} </style></defs>
                <path class="cls-1" d="M4,379l137-67L124,169l150,5L330,30l129,76L571,3l84,127L796,94l14,150,148,35L901,420l108,96L895,612l51,138L804,789,786,931,637,895l-84,122L448,921,312,982,262,841l-147-1,20-147L9,625,94,505Z"/>
                <path class="cls-2" d="M274.388,604.066l39.551-3.076-3.223-204.053-48.34,1.9,6.3,131.4-93.6-133.594H132.445V606.7h56.4l-2.929-127.149ZM505.535,447.035v-50.1H335.466L338.1,606.7,488.4,604.066l-1.172-39.99-95.068,3.076L391.57,544.3h62.988V516.175H390.4l-0.879-69.14H505.535Zm167.412-56.194-30.908-2.49L603.074,514.767,574.8,388.351l-58.154,6.885L566.16,599h51.562l43.8-124.219,30.615,116.748,46.582,5.127,53.028-197.461-49.512-8.936L707.517,528.244Zm186.136,10.637-42.48-2.051-5.42,136.231,35.6,2.051ZM802.76,593.519a22.738,22.738,0,0,0,5.567,6.812,26.571,26.571,0,0,0,7.763,4.467,25.132,25.132,0,0,0,8.863,1.612,26.773,26.773,0,0,0,16.919-6.079,22.811,22.811,0,0,0,5.566-6.812,21.084,21.084,0,0,0,2.417-8.789,24.029,24.029,0,0,0-1.318-8.569,21.982,21.982,0,0,0-4.688-7.837,24.749,24.749,0,0,0-7.983-5.713,24.381,24.381,0,0,0-10.913-2.051,24.623,24.623,0,0,0-17.8,7.764,24.4,24.4,0,0,0-6.519,16.406A18.277,18.277,0,0,0,802.76,593.519Z"/></svg>`
            }

            //Item Box
            var item_box = `<div class='item-box' id=${video['yt_video_id']} data-filters="${filter_string}">
                                ${yt_video_new_flag}
                                <div class="item-wrap">
                                    <div class="item-box-img">${resource_type_flag_string}
                                        <a href="https://youtube.com/channel/${video['yt_channel_id']}"><img class="item-box-logo logo-absolute" src="${video["yt_channel_image"]}"></img></a>
                                        <div class="item-flag-container">${tf_map_flag_string}${tf_class_flag_string}${mrtf_votes_sum_flag_string}</div>
                                        <img class="item-box-img-select" data-yt_video_id=${video['yt_video_id']} src="https://i.ytimg.com/vi/${video['yt_video_id']}/${thumbnail_resolution}.jpg" loading="lazy"></img>
                                    </div>
                                    <div class="item-box-caption">
                                        <div class="caption-top"><span
                                                class="item-box-creator">${display_name}</span>${yt_views_string}${time_ago_string}</div>
                                        <span class="item-box-title" title=${video['yt_video_title']}>${video['yt_video_title']}</span>
                                    </div>
                                </div>
                            </div>`;

            $('#item-boxes-container').append(item_box);
            //$('#item-boxes-container').append(`<div class='item-box' style='height:100px;width:316px;background-color:red; margin:0px;' data-filters='map-orange'></div>`);

        });

}).done(function(){
    //Initialize Isotope on listing container after loading all listings
    $(".item-boxes-container").dynamicGrid({
        "isotopeArgs": {
            transitionDuration: 0,
            fitWidth: true,
            layoutMode: 'masonry'},
        "width": 316,
        "height": 228,
        "itemsSelector": ".item-box"
    });
    
    filterListings();
})
}

//Text formatting functions

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
                tag_select_class = ``
                if(counts['user']){tag_select_class = `tag-selected`}
                tag_items += `<div class="tag-button item-flag ${tag_select_class}" data-tag="${tag}">${tag} <span class="tag-count">x ${counts['count']}</span></div>`
                common_tags.splice( $.inArray(tag, common_tags), 1 );
                
            })
            

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
    YT.get('iframe-holder').loadVideoByUrl({'mediaContentUrl':`http://www.youtube-nocookie.com/embed/${yt_video_id}${clip_string}`})
}

function onPlayerReady(event) {
    if($.modal.isActive()){
        var m = $.modal.getCurrent().options;
        loadVideo(m.yt_video_id,m.yt_clip_id,m.yt_clipt)
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





