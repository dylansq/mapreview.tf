function select_map(tf_map_full){
    const ytList = document.getElementById("select_"+tf_map_full)
    fetch(`/button/${tf_map_full}`,{method: "POST"}).then((res) => res.json()).then((data) => console.log(data));
    
    $.post('/', {
        tf_map_full: tf_map_full, // <---- This is the info payload you send to the server.
    }).done(function(data){ // <!--- This is a callback that is being called after the server finished with the request.
        // Here you dynamically change parts of your content, in this case we modify the construction-projects container.
        $('#item-boxes-container').html(data.result.map(item => `
        <iframe id = "myiFrame" width="560" height="315" src="https://www.youtube.com/embed/${yt_id}"
        title="YouTube video player" 
        frameborder="0" 
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
        allowfullscreen>
        </iframe>`))
        
    }).fail(function(){
        console.log('error') // <!---- This is the callback being called if there are Internal Server problems.
    });
    
    console.log(tf_map_full);
    
}

function getYoutubeStats(yt_id){
    $.getJSON(`https://gdata.youtube.com/feeds/api/videos/${yt_id}?v=2&alt=json`,function(data) {
        console.log( data );
      })
        .done(function() {
          console.log( "second success" );
        })
    
}




//Handel map buttons
$(document).ready( function() { 
    var $yt_iframes = $('#item-boxes-container');
    $('.map-button').each(function () {
        var $this = $(this);
        $this.on("click", function () {
            //alert($(this).data('tf_map_full'));
            $.post("/tf_map_select", {"tf_map_full": $(this).data('tf_map_full')
            }).done(function(data){ // <!--- This is a callback that is being called after the server finished with the request.
                    // Here you dynamically change parts of your content, in this case we modify the construction-projects container.
                    var elements = $();
                    
                    var $yt_id = $();
                    for(let i = 0; i < data["yt_ids"].length; i++) {
                        var $yt_id = data["yt_ids"][i];
                        //stats = execute(data["yt_ids"][i]);
                        console.log($yt_id);
                        //var iframe_object = `<iframe id = "${data["yt_ids"][i]}" width="560" height="315" src="https://www.youtube.com/embed/${data["yt_ids"][i]}?rel=0" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen> </iframe><li>${stats.viewCount}</li>`;
                        //var iframe_object = `<img id = ${data["yt_ids"][i]} class="yt-embed-image" src='https://img.youtube.com/vi/${data["yt_ids"][i]}/hq720.jpg'></img>`;
                        var iframe_object = `<div class="embed-youtube" data-id="${data['yt_ids'][i]}" width="400px" height="320px"></div>`;
                        

                        elements = elements.add(iframe_object);
                        
                        
                    }
                    
                    $('#item-boxes-container').empty();
                    $('#item-boxes-container').append(elements);
                    $('.embed-youtube').embedVideo(width = "230px");
                
            }).fail(function(){
                console.log('error') // <!---- This is the callback being called if there are Internal Server problems.
            });

    });
});
})
$(document).ready( function() {
    updateItemBoxes();
});

function updateItemBoxes(){
    $(document).ready( function() {
        const urlParams = new URLSearchParams(window.location.search);
        const myParam = urlParams.get('myParam');
        console.log(urlParams.toString());
        const queryString = window.location.search;
        $.get("/tf_map_select_get"+queryString,function(data){ // <!--- This is a callback that is being called after the server finished with the request.
                    // Here you dynamically change parts of your content, in this case we modify the construction-projects container.
                    console.log(data)
                    var elements = $();
                    
                    var $yt_id = $();
                    for(let i = 0; i < data["yt_ids"].length; i++) {
                        var $yt_id = data["yt_ids"][i];
                        var $yt_id = data["st_creators"][i];
                        //stats = execute(data["yt_ids"][i]);
                        console.log($yt_id);
                        //var iframe_object = `<iframe id = "${data["yt_ids"][i]}" width="560" height="315" src="https://www.youtube.com/embed/${data["yt_ids"][i]}?rel=0" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen> </iframe><li>${stats.viewCount}</li>`;
                        //var iframe_object = `<img id = ${data["yt_ids"][i]} class="yt-embed-image" src='https://img.youtube.com/vi/${data["yt_ids"][i]}/hq720.jpg'></img>`;
                        var iframe_object = `<div><div class="embed-youtube" data-id="${data['yt_ids'][i]}" width="300px" height="158px"></div><span">${data['st_creators'][i]}</span></div>`;
                        

                        elements = elements.add(iframe_object);
                        
                        
                    }
                    
                    $('#item-boxes-container').empty();
                    $('#item-boxes-container').append(elements);
                    $('.embed-youtube').embedVideo(width = "300px");
                
            }).fail(function(){
                console.log('get fail') // <!---- This is the callback being called if there are Internal Server problems.
            });

})};


$("button").click(function(){
    var iframe = $("#myiFrame");
    iframe.attr("src", iframe.data("src")); 
});

document.querySelector("iframe").addEventListener( "load", function(e) {
    let frameElement = document.getElementById("test");

    this.style.width = 200;
    

    console.log("iframe");

} );    

//$('#creators').selectize();
//$('#maps').selectize();



window.onload = function() {
    let frameElement = document.getElementById("test");
    console.log(frameElement)
  }