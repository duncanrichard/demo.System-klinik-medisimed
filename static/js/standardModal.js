function showModal(data)
{
	buildModal(data);
	$('#standard_modal').modal({backdrop: 'static', keyboard: false, show:true});
}
function hideModal()
{
	$('#standard_modal').unbind('click');
	$('#standard_modal').modal('hide');
}
function buildModal(data)
{
	$('#modal_label').html(data.title);
	$('#standard_modal .close').show();
	if(data.option)
	{
		if(data.option.dismissable == false)
		{
			$('#standard_modal .close').hide();
		}
	}
	if(data.form)
	{
		$('#modal_form').attr({
			'class' : data.form.class,
			'onclick' : data.form.onclick,
			'action' : data.form.action,
			'method' : data.form.method,
		})	
	}

	$('#modal_body').html('');
	console.log('body kuuu')
	if(data.body)
	{
		$('#modal_body').attr({
			'class' : data.body.class,
		})
		$('#modal_body').html(data.body.content)	
		console.log('body kuuu')
		$('#modal_body').show();
	}
	

	$('#modal_footer').html('');
	if(data.footer)
	{
		$('#modal_footer').attr({
			'class' : data.footer.class,
		})
		$('#modal_footer').html(data.footer.content)
		var btnDom = '';
		for (var i = data.footer.button.length - 1; i >= 0; i--) {
			var btn = data.footer.button[i] ;
			var tag = (btn.tag)? btn.tag :'button';
			var btnColor = (btn.color)? btn.color :'default';
			var btnClass = (btn.class)?'class="'+btn.class+' btn btn-'+btnColor+'"':'class="btn btn-'+btnColor+'"';
			var btnId = (btn.id)?'id="'+btn.id+'"':"";
			var btnType = (btn.type)?'type="'+btn.type+'"':"";
			var btnOnclick = (btn.onclick)?'onclick="'+btn.onclick+'"':"";
			var btnHref = (btn.href)?'href="'+btn.href+'"':"";
			var btnDismiss = (btn.dismiss)?'data-dismiss="modal"' : '';
			var strdom = "<"+tag+" "+btnId+" "+btnClass+" "+btnHref+" "+btnOnclick+" "+btnType+" "+btnDismiss+"> "+btn.text+" </"+tag+">";
			btnDom += strdom;
		}
		$('#modal_footer').append(btnDom);
		$('#modal_footer').show();
	}

	if(data.onClose)
	{
		$('#standard_modal').on('hidden.bs.modal', function () {
			// do something…
			data.onClose()
		})
	}else
	{
		$('#standard_modal').unbind('hidden.bs.modal')
	}
	
}

function startLoading(){
    showModal({
        option:{
            dismissable : true,
        },
        title : "Sedang di Proses...",
        body : {
            content : '<div class="sk-spinner sk-spinner-fading-circle"><div class="sk-circle1 sk-circle"></div><div class="sk-circle2 sk-circle"></div><div class="sk-circle3 sk-circle"></div><div class="sk-circle4 sk-circle"></div><div class="sk-circle5 sk-circle"></div><div class="sk-circle6 sk-circle"></div><div class="sk-circle7 sk-circle"></div><div class="sk-circle8 sk-circle"></div><div class="sk-circle9 sk-circle"></div><div class="sk-circle10 sk-circle"></div><div class="sk-circle11 sk-circle"></div><div class="sk-circle12 sk-circle"></div></div>',
        },
    });
}
