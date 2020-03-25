$(function(){

function showFlash(msg, type) {
    $('#flash-box').html(`
        <p class="bg-${type}">${msg}</p>
    `)
}


$.ajax({
    url: "/myfiles",
    method: 'GET'
    })
    .done((res) => {
        getTaskResult(res.task_id, showUpdData)
    });

$('.upload-form').ajaxForm({
    error: function(res){
        showFlash(JSON.parse(res.responseText).error, 'danger');
    },
    success: function(res) {
        getTaskResult(res.task_id, showUpdData);
    }
});

var elemId;
$(document).on("submit", ".delete-form", function() {
    $(this).ajaxSubmit({
        beforeSerialize: function($form, options) {
            elemId = $form.parent().parent().attr('id');
        },
        success: function(res) {
            getTaskResult(res.task_id, updDeletedData, elemId)
        }
    });
    return false;
});

$(document).on("submit", ".download-form", function() {
    $(this).ajaxSubmit({
        success: function(res) {
            getTaskResult(res.task_id, goToDownload)
        }
    });
    return false;
});


function goToDownload(resp, elemId) {
    try {window.location.replace(resp.data.url);}
    catch(e) { window.location = resp.data.url; }
}

function updDeletedData(resp, elemId){
    $('#'+elemId).remove();
}

function showUpdData(resp, formId){
    var new_id = parseInt($("#mainTable tr:last").attr('id'))+1;
    var row = "";
    var fileList = JSON.parse(resp.data.file_list);
    fileList.forEach(function (el) {
        row += `
          <tr id="${new_id}">
            <td>${el.file_name}</td>
            <td>${el.size}</td>
            <td>${el.last_modified}</td>
            <td class="td-buttons">
                <form class="delete-form" action="/myfiles/${el.key}/delete"
                      method="POST">
                    <input name="csrf_token" type="hidden" value="${resp.csrf_token}">
                  <button type="submit" class="btn btn-danger btn-sm">
                      <span class="glyphicon glyphicon-trash"></span>
                  </button>
                </form>
                <form class="download-form" action="/myfiles/${el.key}/download"
                      method="GET">
                  <button type="submit" class="btn btn-default btn-sm">
                      <span class="glyphicon glyphicon-download-alt"></span>
                  </button>
                </form>
            </td>
          </tr>`;
        new_id += 1;
    });
    $("#mainTable tr:first").after(row);
}

function getTaskResult(taskID, dataUpdater, formId) {
  $.ajax({
    url: `/tasks/${taskID}`,
    method: 'GET',
    statusCode: {
        200: function (res) {
            if (res.data.hasOwnProperty('error')){
                showFlash(res.data.error, 'danger');
            } else {
                if (res.data.hasOwnProperty('success')){
                    showFlash(res.data.success, 'info');
                }
                dataUpdater(res, formId);
            }
        },
        202: function (res) {
            setTimeout(function() {
              getTaskResult(taskID, dataUpdater, formId);
            }, 1000);
        }
    }
  })
  .fail((err) => {
    console.log(err);
  });
}

});

