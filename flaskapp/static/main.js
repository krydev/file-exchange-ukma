$(function(){

$.ajax({
    url: "/myfiles",
    method: 'GET'
    })
    .done((res) => {
        getTaskResult(res.task_id, showUpdData)
    });

$('.upload-form').ajaxForm({
    success: function(res) {
          getTaskResult(res.task_id, showUpdData)
    }
});

var elemId;
$(document).on("submit", ".delete-form", function() {
    $(this).ajaxSubmit({
        beforeSerialize: function($form, options) {
            elemId = $form.parent().parent().attr('id');
        },
        success: function(res) {
            console.log(elemId);
            getTaskResult(res.task_id, updDeletedData, elemId)
        }
    });
    return false;
});

$(document).on("submit", ".download-form", function() {
    $(this).ajaxSubmit({
        success: function(res) {
            console.log('Going to dowwonload');
            getTaskResult(res.task_id, goToDownload)
        }
    });
    return false;
});


// $('.delete-form').ajaxForm({
//     beforeSerialize: function($form, options) {
//         elemId = $form.parent().parent().attr('id');
//     },
//     success: function(res) {
//         console.log(elemId);
//         getTaskResult(res.task_id, updDeletedData, elemId)
//     }
// });
//
// $('.download-form').ajaxForm({
//     success: function(res) {
//         console.log('Going to dowwonload');
//         getTaskResult(res.task_id, goToDownload)
//     }
// });

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
            dataUpdater(res, formId);
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

