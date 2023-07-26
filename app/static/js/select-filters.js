
$('#creator').selectize({ 
    valueField: 'value',
    searchField: 'value',
    labelField: 'label',
    dropdownParent:'body',
    plugins: ["clear_button"],
    sortField:{field:'count',direction:'desc'},
    render: {option: function(item, escape) {return `<div class='option'> ${escape(item.label)} (${escape(item.count)}) </div>`;}},
    onChange: function(value) {
        updateSearchParms("creator",value);
        filterListings();
    }});
$('#gamemode').selectize({ 
    valueField: 'value',
    searchField: 'value',
    labelField: 'label',
    dropdownParent:'body',
    plugins: ["clear_button"],
    sortField:{field:'count',direction:'desc'},
    render: {option: function(item, escape) {return `<div class='option'> ${escape(item.label)} (${escape(item.count)}) </div>`;}},
    onChange: function(value) {
        updateSearchParms("gamemode",value);
        filterListings();
    }});
$('#class').selectize({ 
    valueField: 'value',
    searchField: 'value',
    labelField: 'label',
    dropdownParent:'body',
    plugins: ["clear_button"],
    sortField:{field:'count',direction:'desc'},
    render: {option: function(item, escape) {return `<div class='option'> ${escape(item.label)} (${escape(item.count)}) </div>`;}},
    onChange: function(value) {
        updateSearchParms("class",value);
        filterListings();
    }});
$('#map').selectize({ 
    valueField: 'value',
    searchField: ['value','label'],
    labelField: 'label',
    dropdownParent:'body',
    plugins: ["clear_button"],
    sortField:{field:'count',direction:'desc'},
    render: {option: function(item, escape) {return `<div class='option'> ${escape(item.label)} (${escape(item.count)}) </div>`;}},
    onChange: function(value) {
        updateSearchParms("map",value);
        filterListings();
    }});
$('#role').selectize({ 
    valueField: 'value',
    searchField: 'value',
    labelField: 'label',
    dropdownParent:'body',
    plugins: ["clear_button"],
    sortField:{field:'count',direction:'desc'},
    render: {option: function(item, escape) {return `<div class='option'> ${escape(item.label)} (${escape(item.count)}) </div>`;}},
    onChange: function(value) {
        updateSearchParms("role",value)
        filterListings();
    }});
$('#type').selectize({ 
    valueField: 'value',
    searchField: 'value',
    labelField: 'label',
    sortField:{field:'count',direction:'desc'},
    dropdownParent:'body',
    plugins: ["clear_button"],
    
    render: {option: function(item, escape) {return `<div class='option'> ${escape(item.label.replace('+',' '))} (${escape(item.count)}) </div>`;}},

    onChange: function(value) {
        updateSearchParms("type",value);
        filterListings();
    }});
$('#language').selectize({ 
    valueField: 'value',
    searchField: ['value','label'],
    labelField: 'label',
    dropdownParent:'body',
    plugins: ["clear_button"],
    sortField:{field:'count',direction:'desc'},
    render: {option: function(item, escape) {return `<div class='option'> ${escape(item.label)} (${escape(item.count)}) </div>`;}},
    onChange: function(value) {
        updateSearchParms("language",value);
        filterListings();
    },
    onInitialize: function(){
        updateSelectedParms("language");
    }});



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
        $("#more_filters").show();
    }else{
        $("#more_filters").hide();
    }
});


var parameter;
function updateSelectedParms(parameter){
    const searchParams = new URLSearchParams(window.location.search);
    if(searchParams.has(parameter)){
        $('#'+parameter)[0].selectize.setValue(searchParams.get(parameter).toLowerCase());
        
    }
}


function updateSearchParms(parameter,value){
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

