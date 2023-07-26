function filterListings(){
    /**
     * Update Isotope filters and count/update counts for all filters
     */
    $('#item-boxes-container').isotope({
        filter: function(i, item){
            var found = []
            var attribute_string = $(this).attr('data-filters')//region-na,region-eu,gamemode-ultiduo,gamemode-sixes,gamemode-highlander,skill-2,skill-3,
            var search_params = getSearchParms()['dict']
            if(!search_params){return true;}
            var age_found = true;
            if('age' in search_params){
                try{age_found = search_params['age'][0] > parseInt(attribute_string.match(`(,age-).+?(?=,)`)[0].split('-')[1])/30
                }catch{age_found = true
                }}
            found.push(age_found)
            found.push(getSearchParms()['regex'].test(attribute_string))
            return found.every(Boolean);
        }});

    //Initialize filter_counts with all possible values
    var filter_counts = initFilterCounts();
    
    //Add currently filtered items
    $.each($('#item-boxes-container').isotope('getFilteredItemElements'),function(i,item){
        $.each(item.dataset['filters'].split(','),function(i,filter){
            if(filter){
                var fv = filter.split('-')
                var param = fv[0]
                var value = String(fv[1])
                if(param == 'age'){return;}
                if(value in filter_counts[param]){
                    filter_counts[param][value] += 1
                }else{
                    filter_counts[param][value] = 1
                }

                
            }
        
        
        });
    });
    
    //SELECTIZE
    $.each(filter_counts,function(parameter,counts){
        if(parameter == 'age'){return;}
        $.each(counts, function(label,count) {
            if(parameter == 'age'){return;}
            else if(parameter == 'creator'){
                $('#'+parameter)[0].selectize.addOption({'count':count,'label':label.replace('+',' '),'value':label.replace('+',' ').toLowerCase()});}
            else{
                $('#'+parameter)[0].selectize.addOption({'count':count,'label':label.replace('+',' '),'value':label.replace('+',' ').replace('_',' ').toLowerCase()});}
            //$('#'+parameter)[0].selectize.refreshOptions();
            //$('#type')[0].selectize.updateOption({count:count,label:label})
            //console.log({'count':count,'label':label,'value':label})
           
            //Update selectize options from url now that everything is loaded
            updateSelectedParms(parameter);
        });
    });

    //updateAllMultiSelectCounts(filter_counts)
    return;
}

function initFilterCounts(){
    /**
     * Initializes the filter_counts dictionary which contains a count of each possible filter
     */
    var filter_counts = {}
    var all_items = $('#item-boxes-container').isotope('getItemElements')
    $.each(all_items,function(i,item){
        $.each(item.dataset['filters'].split(','),function(i,filter){
            if(filter){
                var fv = filter.split('-')
                var param = fv[0]
                var value = String(fv[1])
                if(param == 'age'){return;}
                try{
                    filter_counts[param][value] = 0
                }catch{
                    filter_counts[param] = {}
                    filter_counts[param][value] = 0
                }
            }
        })
    });
    return filter_counts
};



function getSearchParms(){
    /**
     * Returns the regex matching string for current search query param/values used to filter listings
     */
    var searchParams = window.location.search.replace('?','');
    param_list = searchParams.split('&')
    if(param_list[0] == ''){
        return {};
    }
    var param = ''
    var data = ''
    var param_dict = {}
    var param_reg_string = ''
    
    param_list.forEach(function(item,index){
        items = item.split('=')
        param = items[0]
        data = items[1]
        param_dict[param] = data.split('%7E') //split on `~` %7E

        if(param=='age'){ 
            return;
        }
        else{
            param_reg_string += '(?=.*'+param+'-('+data.replace('+','\\+').replace('%7E','|')+'))'
        }

    });
    var parm_regex = new RegExp(param_reg_string,'gi')
    return {'regex':parm_regex,'dict':param_dict}
}




function updateSearchParms(parameter, value, concatParams) {
    /**
     * Updates URL search query parameters
     * @param {String} parameter - Parameter to update (ex. 'status')
     * @param {String} value - Value of the parameter to update, if the value alreay is in the query string, remove the value
     * @param {Boolean} parameter - If the parameter is already in the query string, conatenate with existing values using '~'
     */
    var searchParams = new URLSearchParams(window.location.search);
    var locationPath = window.location.pathname
    try{value = value.replace(' ', "+").replace('%2B', "+").toLowerCase();}
    catch{}
    if (searchParams.has(parameter) && concatParams) {
        //Parameter exists and user wants to concat
        var searchParamsArray = searchParams.get(parameter).split('~')
        searchParamsArray = searchParamsArray.filter(function (v) { return v !== 'd'; });
        indexParameter = searchParamsArray.indexOf(value)
        if (indexParameter != -1) {
            //exists in array, remove
            searchParamsArray.splice(indexParameter, 1)
        } else {
            searchParamsArray.push(value)
        }
        var searchParamsString = searchParamsArray.join('~');
        
        if (searchParamsString != '') {
            searchParams.set(parameter, searchParamsString);
        } else {
            searchParams.delete(parameter)
        }
        
    } else {
        searchParams.set(parameter, value)
    }
    if(searchParams.get(parameter) == ''){
       
        searchParams.delete(parameter)
    }
    if (Array.from(searchParams).length == 0) {
        //No Search Queries, remove search decorator
        window.history.replaceState({}, '', `${locationPath}`);
    } else { window.history.replaceState({}, '', `${locationPath}?${searchParams.toString().replace('%2B', "+")}`); }
}


//Add filtering/selecting functions to each search option
$(".region-select, .flag.region-select").click(function (e) {
    var region_selected = $(this).data()['region']
    updateMultiselectParameters($(this),e,'region',region_selected,'region-selected','region-unselected',select_class='region-select')
    $('.listing-container').isotope({filters: filterListings()})
});

$(".skill-select").click(function (e) {
    var skill_selected = $(this).data()['skill']
    updateMultiselectParameters($(this),e,'skill',skill_selected,'skill-selected','skill-unselected', 'skill-select', null)
    $('.listing-container').isotope({filters: filterListings()})
});

$(".flag-select").click(function (e) {
    var param_selected = $(this).data()['param']
    var value_selected = $(this).data()['value']
    updateMultiselectParameters($(this),e,param_selected,value_selected,'flag-selected','flag-unselected',null, param_selected)
    $('.listing-container').isotope({filters: filterListings()})
});


//Update Selectize search dropdowns
function updateMultiSelectCounts(parameter,values){
    $.each(values,function(value,dict){
        $('#'+parameter+'-select-count-'+dict.value).text('['+dict.count+']');
        if(dict.count == 0 && parameter!='region'){
            $('#'+parameter+'-select-count-'+dict.value).parent().addClass('select-hide')
    }else{
        $('#'+parameter+'-select-count-'+dict.value).parent().removeClass('select-hide')
    }
});
}

function updateAllMultiSelectCounts(filter_counts){
    /**
     * @param {Object} filter_counts - two level dictionary, eg {'gamemode':{'sixes':0}} specifying number of filtered results available
     */
    $.each(filter_counts,function(parameter,counts){
        $.each(counts,function(value,count){
            $('#'+parameter+'-select-count-'+value).text('['+count+']');
            if(count == 0 && parameter!='region'){
                $('#'+parameter+'-select-count-'+value).parent().addClass('select-hide')
        }else{
            $('#'+parameter+'-select-count-'+value).parent().removeClass('select-hide')
        }
    });
    })
    
}
function updateMultiselectParameters(this_,event, parameter_selected, value_selected, selected_class,unselected_class, select_class = null, select_data_parameter = null){
    /**
     * Handels multiple selecting, shift+selecting of filter options
     * @param {Object} this_ - $(this)
     * @param {Event} event - Click event, e
     * @param {String} parameter_selected - Parameter to filter on
     * @param {String} value_selected - Value of the parameter to filter on
     * @param {String} selected_class - HTML class specifying a filter button was selected
     * @param {String} unselected_class - HTML class specifying a filter button is not selected (disabled)
     * @param {String} [select_class=null] - Class used to select the filter button, need to specify either select_class or select_data_parameter
     * @param {String} [select_data_parameter=null] - Data parameter used to select the filter button, need to specify either select_class or select_data_parameter
     * 
     */
    //custom handler for mutiselect events with shift click support
    if(select_class){
        var select_selector = '.'+select_class
    }else if (select_data_parameter){
        var select_selector = `div[data-param="${select_data_parameter}"]`
    }else{
        alert('no selector declared')
    }

        
    if (this_.hasClass(selected_class)) {
        //this option was already selected, reset all options
        if (event.shiftKey) {
            //User de-selecting just this option
            this_.addClass(unselected_class)
            this_.removeClass(selected_class)
            updateSearchParms(parameter_selected, String(value_selected), true)
    
        } else {
            //Reset all options
            $(select_selector).removeClass(unselected_class)
            $(select_selector).removeClass(selected_class)
            updateSearchParms(parameter_selected, '')
        }
    } else if (this_.hasClass(unselected_class)) {
        //User has already selected another option, don't reset though
        if (event.shiftKey) {
            //User is adding selected item to another selected item
            this_.removeClass(unselected_class)
            this_.addClass(selected_class)
            updateSearchParms(parameter_selected, String(value_selected), true)
        } else {
            //Switch only selected item to this item
            $(select_selector).addClass(unselected_class);
            $(select_selector).removeClass(selected_class);
            this_.removeClass(unselected_class);
            this_.addClass(selected_class);
            updateSearchParms(parameter_selected, String(value_selected));
        }
    } else {
        //User has not selected any items
        $(select_selector).addClass(unselected_class)
        this_.removeClass(unselected_class)
        this_.addClass(selected_class)
        updateSearchParms(parameter_selected, String(value_selected))
    }



}



//Helper Functions
const age_breaks = [1,3,6,12,24,36,36,48,60,72,84,96,108,120,180]//months
$('.slider-container').on('change', '#age-slider', function() {
    if(age_breaks[$(this).val()]<180){
        updateSearchParms('age',age_breaks[$(this).val()])
    }else{
        updateSearchParms('age','')
    }
    filterListings();
  });


$('.slider-container').on('input', '#age-slider', function() {
    var age_months = age_breaks[$(this).val()]
    var remainder_months = age_months % 12
    var remainder_years = Math.floor(age_months/12)
    var age_string = ``
    if(remainder_months != 0){age_string += `${remainder_months} months`;}
    if(remainder_years != 0){age_string += `${remainder_years} years`;}
    if(remainder_years>=15){age_string = `All`}
    $('#age-slider-value').html(age_string);
});










