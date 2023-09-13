const ht_table = $('#hacker_table').DataTable({
    order: [[12, 'desc']],
    lengthMenu: [[-1,50,25],['All',50,25]],
    columnDefs: [
        { 
            targets: [4,5,6,7],
            render: function (data,type,row) {
            if (data == "True") {
              return '<input type="checkbox" checked onclick="return false;"/>';
            } else {
              return '';
            }
        } }
    ]
    });

ht_table.on('click', 'tbody tr', (e) => {
    let classList = e.currentTarget.classList;
    if (classList.contains('selected')) {
        classList.remove('selected');
    }
    else {
        ht_table.rows('.selected').nodes().each((row) => row.classList.remove('selected'));
        classList.add('selected');
    }
});


$("#update_steamrep").click(function(){

console.log('updating steam rep')

$.get("/ht/ht_update_all_steamrep")
  
});


$("#update_all_steam").click(function(){
$.get("/ht/ht_update_all_steam")
});

function SteamID64To3(st_id64){
    var steamID64IDEnt = 76561197960265728
    var id3base = st_id64 - steamID64IDEnt
    return (["[U:1:"+id3base+"]",id3base])
}


$("#update_rich_presence").click(function(){
    $.get("/ht/ht_get_all_rich_presence")

});

$("#confirm_hacker").click(function(e){
    console.log($(this).attr('data-id'))
    console.log({'st_id64':$(this).attr('data-id')})
    $.post("/ht/confirm_hacker",{'st_id64':$(this).attr('data-id')}).done(function(res){
        alert(res)
        location.reload();
      }).fail(function(err){
          alert(err.responseText)
          console.log(err.responseText)
      });

});

$("#deny_hacker").click(function(e){
    $.post("/ht/confirm_hacker",{'st_id64':$(this).attr('data-id')}).done(function(res){
        alert(res)
        location.reload();
      }).fail(function(err){
          alert(err.responseText)
          console.log(err.responseText)
      });
});

$(".remove_hacker").click(function(e){
    console.log($(this).attr('data-id'))
    console.log({'st_id64':$(this).attr('data-id')})
    $.post("/ht/remove_hacker",{'st_id64':$(this).attr('data-id')}).done(function(res){
        alert(res)
        location.reload();
      }).fail(function(err){
          alert(err.responseText)
          console.log(err.responseText)
      });

});

$("#ht_form_submit").click(function(event){
event.preventDefault();
console.log($('#ht_submit').serializeArray())
var form_data = $('#ht_submit').serializeArray().reduce(function(obj, item) {obj[item.name] = item.value; return obj;}, {});
$.post("/ht/submit_hacker",form_data).done(function(){
  alert("Account submitted successfully")
  //location.reload();
}).fail(function(err){
    alert(err.responseText)
    console.log(err.responseText)
});
return false
});

$("#check_id").click(function(event){
event.preventDefault();
$.get("/ht/check_existing_hackers?st_id64="+$('#st_id64').val()).done(function(){
  $('#ht_form_submit').prop("disabled", false);
}).fail(function(err){
    alert(err.responseText)
    console.log(err.responseText)
});
});

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