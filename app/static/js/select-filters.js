$(function(){
    $('#creators').selectize({
        dropdownParent:'body',
        plugins: ["clear_button"],
        onChange: function(value) {
            updateSearchParms("creators",value);
            updateItemBoxes();
        },
        onInitialize: function(){
            updateSelectedParms("creators");
        }});
    $('#format').selectize({ 
        valueField: 'value',
        searchField: 'value',
        labelField: 'label',
        dropdownParent:'body',
        plugins: ["clear_button"],
        render: {option: function(item, escape) {return `<div class='option'> ${escape(item.label)} (${escape(item.count)}) </div>`;}},
        onChange: function(value) {
            //updateSearchParms("format",value);
            if(window.location.origin + window.location.pathname != window.location.origin +"/"+value){
                window.location = window.location.origin +"/"+value
            }
            //updateItemBoxes();
        },
        onInitialize: function(){
            if(window.location.pathname.length >2){
                console.log('changing format' + window.location.pathname.substring(1) )
                $('#format')[0].selectize.setValue(window.location.pathname.substring(1));
            }
            
            //updateSelectedParms("format");
        }});
    $('#class').selectize({ 
        valueField: 'value',
        searchField: 'value',
        labelField: 'label',
        dropdownParent:'body',
        plugins: ["clear_button"],
        render: {option: function(item, escape) {return `<div class='option'> ${escape(item.label)} (${escape(item.count)}) </div>`;}},
        onChange: function(value) {
            updateSearchParms("class",value);
            updateItemBoxes();
        },
        onInitialize: function(){
            updateSelectedParms("class");
        }});
    $('#map').selectize({ 
        valueField: 'value',
        searchField: ['value','label'],
        labelField: 'label',
        dropdownParent:'body',
        plugins: ["clear_button"],
        render: {option: function(item, escape) {return `<div class='option'> ${escape(item.label)} (${escape(item.count)}) </div>`;}},
        onChange: function(value) {
            updateSearchParms("map",value);
            updateItemBoxes();
        },
        onInitialize: function(){
            updateSelectedParms("map");
        }});
    $('#role').selectize({ 
        valueField: 'value',
        searchField: 'value',
        labelField: 'label',
        dropdownParent:'body',
        plugins: ["clear_button"],
        render: {option: function(item, escape) {return `<div class='option'> ${escape(item.label)} (${escape(item.count)}) </div>`;}},
        onChange: function(value) {
            updateSearchParms("role",value)
            updateItemBoxes();
        },
        onInitialize: function(){
            updateSelectedParms("role");
        }});
    $('#type').selectize({ 
        valueField: 'value',
        searchField: 'value',
        labelField: 'label',
        
        dropdownParent:'body',
        plugins: ["clear_button"],
        
        render: {option: function(item, escape) {return `<div class='option'> ${escape(item.label)} (${escape(item.count)}) </div>`;}},

        onChange: function(value) {
            updateSearchParms("type",value);
            updateItemBoxes();
        },
        onInitialize: function(){
            updateSelectedParms("type");
        }
    });
    $('#language').selectize({ 
        dropdownParent:'body',
        plugins: ["clear_button"],
        onChange: function(value) {
            updateSearchParms("language",value);
            updateItemBoxes();
        },
        onInitialize: function(){
            updateSelectedParms("language");
        }
    });
});

//update checkbox on load if needed
$(function(){
    const searchParams = new URLSearchParams(window.location.search);
    if(searchParams.has("showclips")){
        $("#checkbox_show_clips").toggleClass("checkbox-yes");
    }
});

$("#checkbox_show_clips").click(function(){
    $( this ).toggleClass("checked")
    if($( this ).hasClass("checked")){
        updateSearchParms("showclips","")
    }else{
        updateSearchParms("showclips","false")
    }
});

$("#checkbox_show_morefilters").click(function(){
    $( this ).toggleClass("checked")
    if($( this ).hasClass("checked")){
        console.log('here')
        $("#more_filters").show();
    }else{
        $("#more_filters").hide();
    }
});


var parameter;
function updateSelectedParms(parameter){
    const searchParams = new URLSearchParams(window.location.search);
    if(searchParams.has(parameter)){
        console.log("parametera: " + parameter)
        console.log(searchParams.get(parameter))
        $('#'+parameter)[0].selectize.setValue(searchParams.get(parameter));
    }
}

function updateOptionCounts(){
    
}




function updateSearchParms(parameter,value){
    console.log(value)
    const searchParams = new URLSearchParams(window.location.search);
    var locationPath = window.location.pathname
    if(value == ''){
        searchParams.delete(parameter);
    }else{
        searchParams.set(parameter, value);
    }
    if(Array.from(searchParams).length == 0){
        window.history.replaceState({}, '', `${locationPath}`);
    }else{window.history.replaceState({}, '', `${locationPath}?${searchParams.toString()}`);}
    
}

