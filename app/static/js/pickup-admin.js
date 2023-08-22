
function test(server){
    console.log(server)
    

    $('#ptf_region').selectize({
        plugins: ["remove_button"],
        delimiter: ',',
        persist: false,
        valueField:"field",
        labelField:"region",
        options:[
            {region:"North America",region2:"NA",field:"ptf_region_na",value:true},
            {region:"South America",region2:"SA",field:"ptf_region_sa",value:true},
            {region:"Europe",region2:"EU",field:"ptf_region_eu",value:true},
            {region:"Asia",region2:"AS",field:"ptf_region_as",value:true},
            {region:"Africa",region2:"AF",field:"ptf_region_af",value:true},
            {region:"Oceania",region2:"OC",field:"ptf_region_oc",value:true}
        ],
        
        onDelete: function(values) {
          return confirm(values.length > 1 ? 'Are you sure you want to remove these ' + values.length + ' items?' : 'Are you sure you want to remove "' + values[0] + '"?');
        }
      });


      $('.ptf_region').selectize({
        plugins: ["remove_button"],
        delimiter: ',',
        persist: false,
        valueField:"field",
        labelField:"region",
        options:[
            {region:"North America",region2:"NA",field:"ptf_region_na",value:true},
            {region:"South America",region2:"SA",field:"ptf_region_sa",value:true},
            {region:"Europe",region2:"EU",field:"ptf_region_eu",value:true},
            {region:"Asia",region2:"AS",field:"ptf_region_as",value:true},
            {region:"Africa",region2:"AF",field:"ptf_region_af",value:true},
            {region:"Oceania",region2:"OC",field:"ptf_region_oc",value:true}
        ],
        
        onDelete: function(values) {
          return confirm(values.length > 1 ? 'Are you sure you want to remove these ' + values.length + ' items?' : 'Are you sure you want to remove "' + values[0] + '"?');
        }
      });

      region = []
      $.each($('.ptf_region').selectize()[0].selectize.options, function(opt){
        if(server[opt]){
            console.log(opt)
            region.push(opt)
        }
      })
      $('#ptf_region_155').selectize()[0].selectize.setValue(region)
      //$('#ptf_region').selectize.setValue
      return null
}


const discord_icon = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-discord" viewBox="0 0 16 16"><path d="M13.545 2.907a13.227 13.227 0 0 0-3.257-1.011.05.05 0 0 0-.052.025c-.141.25-.297.577-.406.833a12.19 12.19 0 0 0-3.658 0 8.258 8.258 0 0 0-.412-.833.051.051 0 0 0-.052-.025c-1.125.194-2.22.534-3.257 1.011a.041.041 0 0 0-.021.018C.356 6.024-.213 9.047.066 12.032c.001.014.01.028.021.037a13.276 13.276 0 0 0 3.995 2.02.05.05 0 0 0 .056-.019c.308-.42.582-.863.818-1.329a.05.05 0 0 0-.01-.059.051.051 0 0 0-.018-.011 8.875 8.875 0 0 1-1.248-.595.05.05 0 0 1-.02-.066.051.051 0 0 1 .015-.019c.084-.063.168-.129.248-.195a.05.05 0 0 1 .051-.007c2.619 1.196 5.454 1.196 8.041 0a.052.052 0 0 1 .053.007c.08.066.164.132.248.195a.051.051 0 0 1-.004.085 8.254 8.254 0 0 1-1.249.594.05.05 0 0 0-.03.03.052.052 0 0 0 .003.041c.24.465.515.909.817 1.329a.05.05 0 0 0 .056.019 13.235 13.235 0 0 0 4.001-2.02.049.049 0 0 0 .021-.037c.334-3.451-.559-6.449-2.366-9.106a.034.034 0 0 0-.02-.019Zm-8.198 7.307c-.789 0-1.438-.724-1.438-1.612 0-.889.637-1.613 1.438-1.613.807 0 1.45.73 1.438 1.613 0 .888-.637 1.612-1.438 1.612Zm5.316 0c-.788 0-1.438-.724-1.438-1.612 0-.889.637-1.613 1.438-1.613.807 0 1.451.73 1.438 1.613 0 .888-.631 1.612-1.438 1.612Z"/></svg>`
const steam_icon = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-steam" viewBox="0 0 16 16"><path d="M.329 10.333A8.01 8.01 0 0 0 7.99 16C12.414 16 16 12.418 16 8s-3.586-8-8.009-8A8.006 8.006 0 0 0 0 7.468l.003.006 4.304 1.769A2.198 2.198 0 0 1 5.62 8.88l1.96-2.844-.001-.04a3.046 3.046 0 0 1 3.042-3.043 3.046 3.046 0 0 1 3.042 3.043 3.047 3.047 0 0 1-3.111 3.044l-2.804 2a2.223 2.223 0 0 1-3.075 2.11 2.217 2.217 0 0 1-1.312-1.568L.33 10.333Z"/><path d="M4.868 12.683a1.715 1.715 0 0 0 1.318-3.165 1.705 1.705 0 0 0-1.263-.02l1.023.424a1.261 1.261 0 1 1-.97 2.33l-.99-.41a1.7 1.7 0 0 0 .882.84Zm3.726-6.687a2.03 2.03 0 0 0 2.027 2.029 2.03 2.03 0 0 0 2.027-2.029 2.03 2.03 0 0 0-2.027-2.027 2.03 2.03 0 0 0-2.027 2.027Zm2.03-1.527a1.524 1.524 0 1 1-.002 3.048 1.524 1.524 0 0 1 .002-3.048Z"/></svg>`
const website_icon = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-globe" viewBox="0 0 16 16"><path d="M0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8zm7.5-6.923c-.67.204-1.335.82-1.887 1.855A7.97 7.97 0 0 0 5.145 4H7.5V1.077zM4.09 4a9.267 9.267 0 0 1 .64-1.539 6.7 6.7 0 0 1 .597-.933A7.025 7.025 0 0 0 2.255 4H4.09zm-.582 3.5c.03-.877.138-1.718.312-2.5H1.674a6.958 6.958 0 0 0-.656 2.5h2.49zM4.847 5a12.5 12.5 0 0 0-.338 2.5H7.5V5H4.847zM8.5 5v2.5h2.99a12.495 12.495 0 0 0-.337-2.5H8.5zM4.51 8.5a12.5 12.5 0 0 0 .337 2.5H7.5V8.5H4.51zm3.99 0V11h2.653c.187-.765.306-1.608.338-2.5H8.5zM5.145 12c.138.386.295.744.468 1.068.552 1.035 1.218 1.65 1.887 1.855V12H5.145zm.182 2.472a6.696 6.696 0 0 1-.597-.933A9.268 9.268 0 0 1 4.09 12H2.255a7.024 7.024 0 0 0 3.072 2.472zM3.82 11a13.652 13.652 0 0 1-.312-2.5h-2.49c.062.89.291 1.733.656 2.5H3.82zm6.853 3.472A7.024 7.024 0 0 0 13.745 12H11.91a9.27 9.27 0 0 1-.64 1.539 6.688 6.688 0 0 1-.597.933zM8.5 12v2.923c.67-.204 1.335-.82 1.887-1.855.173-.324.33-.682.468-1.068H8.5zm3.68-1h2.146c.365-.767.594-1.61.656-2.5h-2.49a13.65 13.65 0 0 1-.312 2.5zm2.802-3.5a6.959 6.959 0 0 0-.656-2.5H12.18c.174.782.282 1.623.312 2.5h2.49zM11.27 2.461c.247.464.462.98.64 1.539h1.835a7.024 7.024 0 0 0-3.072-2.472c.218.284.418.598.597.933zM10.855 4a7.966 7.966 0 0 0-.468-1.068C9.835 1.897 9.17 1.282 8.5 1.077V4h2.355z"/></svg>`

function formatDateAgo(date) {
    var startDate = new Date(Date.parse(date));
    var diffDate = new Date(new Date() - startDate);
    var years = diffDate.toISOString().slice(0, 4) - 1970
    var months = diffDate.getMonth()
    var days = diffDate.getDate()-1
    var years_string = ''
    var months_string = ''
    var days_string = ''
    
    if(years >= 2){years_string = `${years} years`}else if(years == 1){years_string = `${years} year`}
    if(months >= 2){months_string = `${months} months`}else if(months == 1){months_string = `${months} month`}
    if(years == 0){
        //first year, show days
        if(days >= 2){days_string = `${days} days`}else if(days == 1){days_string = `${days} day`}
        //if less than 1 week old, overwrite day string with < 1 week
        if(years == 0 && months == 0 && days < 7){day_string = `< 1 week`}
    }
    return `${years_string} ${months_string} ${days_string} old`
}



function createListingItem(key, listing) {
    //Create flags adnd data string
    var region_flag = ``
    var skill_flag = ``
    var gamemode_flag = ``
    var data_string = ``
    var join_string = ``
    var time_string = ``


    //Arrays
    const ptf_regions = { 'na': "North America", 'sa': "South America", 'eu': "Europe", 'as': "Asia", 'oc': "Oceania", 'af': "Africa" }
    const tf_gamemodes = ['ultiduo', 'ultitrio', 'fours', 'sixes', 'prolander', 'highlander']
    const tf_gametypes = ['bball', 'passtime', 'experimental', 'mge', 'mvm']
    const tf_skilllevels = ['0', '1', '2', '3']
    const ptf_server_status_dic = { 1: ["Active", 'active'], 2: ["Inactive", 'inactive'], 3: ["In-Development", 'dev'], 7: ["Other", 'other'], 8: ["Unknown", 'unknown'], 9: ["Dead", 'dead'], 0: ["All", 'all'] }


    $.each(ptf_regions, function (key, val) {
        var variable = 'ptf_region_' + key
        if (listing[variable]) { 
            region_flag += `<span class='flag region-flag'">${val}</span>`;
            data_string += `region-${key},`
        }});

    $.each(tf_gamemodes, function (key, val) {
        var variable = 'tf_gamemode_' + val
        if (listing[variable]) { 
            gamemode_flag += `<span class='flag sixes-flag'">${val}</span>` 
            data_string += `gamemode-${val},`
        }});

    $.each(tf_gametypes, function (key, val) {
        var variable = 'tf_gamemode_' + val
        if (listing[variable]) { 
            gamemode_flag += `<span class='flag sixes-flag'">${val}</span>` 
            data_string += `gametype-${val},`
        }});

    $.each(tf_skilllevels, function (key, val) {
        var tf_skilllevel_var = 'tf_skilllevel_' + val
        if (listing[tf_skilllevel_var]) {
            skill_flag += `<span class='skill-flag skill-flag-${val}' data-skill='${val}'></span>`
            data_string += `skill-${val},`
        } else {
            skill_flag += `<span class='skill-flag skill-flag-${val} skill-flag-none'></span>`
        }});
        if(listing['ptf_site_url']){join_string += `<a href="${listing['ptf_site_url']}"><div class="listing-join listing-website"><div class="listing-icon">${website_icon}</div></div></a>`}
        if(listing['ptf_discord_url']){join_string += `<a href="${listing['ptf_discord_url']}"><div class="listing-join listing-discord"><div class="listing-icon">${discord_icon}</div></div></a>`}
        if(listing['ptf_steamcommunity_url']){join_string += `<a href="${listing['ptf_steamcommunity_url']}"><div class="listing-join listing-steamgroup"><div class="listing-icon">${steam_icon}</div></div></a>`}
                

    data_string += `status-${listing['ptf_server_status']}`

    if(listing['ptf_schedule_day']){
        time_string += `<span class='flag time-flag'>${listing['ptf_schedule_day']} - ${listing['ptf_schedule_time']} ${listing['ptf_schedule_timezone']}</span>`
    }
    var owner_string = ``
    var admin_string = ``
    var mod_string =  ``
    $.each([{'display_name':'Mark Ruffalo','st_id64':'xx','discord_tag':''}],function(i,user){
        owner_string += `<a href='https://steamcommunity.com/profiles/${user['st_id64']}'><span>${user['display_name']}</span><a>`})
    $.each([{'display_name':'Mark Ruffalo','st_id64':'xx','discord_tag':''}],function(i,user){
        admin_string += `<a href='https://steamcommunity.com/profiles/${user['st_id64']}'><span>${user['display_name']}</span><a>`})
    $.each([{'display_name':'Mark Ruffalo','st_id64':'xx','discord_tag':''}],function(i,user){
        mod_string += `<a href='https://steamcommunity.com/profiles/${user['st_id64']}'><span>${user['display_name']}</span><a>`})
    
    

    if(listing['ptf_date_created']){var date_created_string = `<span>${formatDateAgo(listing['ptf_date_created'])}</span>`};
    
    var item_listing = `
    <div class="item-listing" data-filters="${data_string}">
        <div class="listing-main-container">
            <div class="skill-container">${skill_flag}</div>
            <div class="left-container">
                <div class="title-container">
                    <div class="listing-title">${listing['ptf_server_name']}</div>
                    <div class="status-flag status-${ptf_server_status_dic[listing['ptf_server_status']][1]}">${ptf_server_status_dic[listing['ptf_server_status']][0]}</div>
                </div>
                <div class="flag-container">${region_flag}</div>
                <dif class="flag-container">${gamemode_flag}${time_string}</div>
            <div class="right-container">
                <div class="joins-container">${join_string}</div>
            </div>
        </div>
        <div class="listing-description-container">
            <div class="description-age"> Server Age: ${date_created_string}</div>
            <div>Owners: ${owner_string}</div>
            <div>Admins: ${admin_string}</div>   
            <div>Moderators: ${mod_string}</div>
            <div></div>
        </div>
    </div>`;

    return item_listing;
}

function initListings() {
    //Get current URL Search parameters to reference later
    const urlParams = new URLSearchParams(window.location.search);
    var queryString = window.location.search;
    const qs_len = queryString.length

    //GET request to API with current query string
    $.get("https://mapreview.tf/pickup/update_listings", function (data) {
        //Remove previous container contents
        $('#listing-container').empty();

        const ptf_regions = { 'na': "North America", 'sa': "South America", 'eu': "Europe", 'as': "Asia", 'oc': "Oceania", 'af': "Africa" }
        const tf_gamemodes = ['ultiduo', 'ultitrio', 'fours', 'sixes', 'prolander', 'highlander']
        const tf_gametypes = ['bball', 'passtime', 'experimental', 'mge', 'mvm']
        const tf_skilllevels = ['0', '1', '2', '3']
        const ptf_server_status_dic = { 1: ["Active", 'active'], 2: ["Inactive", 'inactive'], 3: ["In-Development", 'dev'], 7: ["Other", 'other'], 8: ["Unknown", 'unknown'], 9: ["Dead", 'dead'], 0: ["All", 'all'] }

        //Iterate over each listing
        $.each(data.results, function (key, listing) {
            var item_listing = createListingItem(key, listing);
            //Add completed listing to container
            $('#listing-container').append(item_listing);
        });

        //Initialize Isotope on listing container after loading all listings
        $('#listing-container').isotope({
            transitionDuration: '0s',
            itemSelector: '.item-listing',
            filter: filterListings()
            
        });

        $('#listing-container').isotope().on('click','.item-listing',function(e){
            
            if (e.target.className =='listing-main-container'){
                var clicked_element =  $(this).find('.listing-description-container')
                $('.listing-description-container').not(clicked_element).hide()
                $(this).find('.listing-description-container').slideToggle(100, function () {
                    $('#listing-container').isotope('layout')
                });
            }
        })
        
        

        $.each(data.counts.lanuage, function (k, v) {
            $('#language')[0].selectize.addOption(v);//Doesn't do anything if value already exists
            $('#language')[0].selectize.updateOption(v.value, v)//Update preexisting values
            //updateMultiSelectCounts()
            updateSelectedParms(parameter)

        });
    });
};




