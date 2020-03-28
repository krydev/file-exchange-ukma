$(function(){
if (window.location.href.includes('#upload')){
    showFlash('File has been uploaded successfully', 'success');
}


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


$(document).on("submit", "#upload-form", function() {
    var file = ($('#file'))[0].files[0];
    if (!file) {
        showFlash('File hasn\'t been selected', 'danger');
    } else {
        $form = $(this);
        $.ajax({
            type: $form.attr('method'),
            url: $form.attr('action'),
            data: {
                'fileSize': file.size,
                 'fileType': file.type, 
                 'fileName': file.name, 
                 'csrf_token': $('#csrf').val()
             }
        }).done(function (res) {
                getTaskResult(res.task_id, uploadFile);
        }).fail(function (res) {
                showFlash(JSON.parse(res.responseText).error, 'danger');
        });
    }
    return false;

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


function uploadFile(resp, formId){
    // populating signature fields
    $('#upload-form input[name="csrf_token"]').remove();
    for(key in resp.data.fields){
        var $sel = $('input[name="'+key+'"]');
        if ($sel.length){
            $sel.val(resp.data.fields[key]);
        }
    }
    $('#upload-form').ajaxSubmit({
        url: resp.data.url,
        processData: false,
        contentType: false,
        resetForm: true,
        xhr: function(){
            var xhr = $.ajaxSettings.xhr();
            xhr.upload.addEventListener('progress', function(evt){
              if(evt.lengthComputable) {
                var percentComplete = Math.ceil(evt.loaded / evt.total * 100);
                showFlash('Uploading ' + percentComplete + '%', 'info');
              }
            }, false);
            return xhr;
        },
        success: function (res) {
            var currUrl = window.location.href;
            var idx = currUrl.indexOf( "#upload" );
            if (idx !== -1){
                currUrl = currUrl.substring(0, idx)
            }
            window.location = currUrl + "#upload";
            window.location.reload();
        },
        error: function (xhr) {
            console.log('Upload error: ' + xhr.responseText);
        }
    });
}

function goToDownload(resp, elemId) {
    window.open(resp.data.url);
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
                    showFlash(res.data.success, 'success');
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

