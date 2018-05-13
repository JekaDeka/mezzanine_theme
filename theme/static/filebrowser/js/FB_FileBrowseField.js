function FileSubmit(FilePath, FileURL, ThumbURL, FileType, BrowseUrl) {

    // var input_id=window.name.split("___").join(".");
    var input_id=window.name.replace(/____/g,'-').split("___").join(".");
    var preview_id = 'image_' + input_id;
    var link_id = 'link_' + input_id;
    var help_id = 'help_' + input_id;
    var clear_id = 'clear_' + input_id;
    var background_id = 'background_' + input_id;
    input = opener.document.getElementById(input_id);
    preview = opener.document.getElementById(preview_id);
    link = opener.document.getElementById(link_id);
    help = opener.document.getElementById(help_id);
    clear = opener.document.getElementById(clear_id);
    background = opener.document.getElementById(background_id);

    // set new value for input field
    input.value = FilePath;

    // enable the clear "button"
    jQuery(clear).css("display", "inline");
    if (link !== null) {
    // link is not null in case of default image field
        if (ThumbURL && FileType !== "") {
            // selected file is an image and thumbnail is available:
            // display the preview-image (thumbnail)
            // link the preview-image to the original image
            link.setAttribute("href", "javascript:FileBrowser.show('" + input_id + "', '"+ BrowseUrl + "');");
            link.setAttribute("target", "_blank");
            link.setAttribute("style", "");
            preview.setAttribute("src", ThumbURL);
            help.setAttribute("style", "");
            jQuery(help).addClass("");
        } else {
            // hide preview elements
            link.setAttribute("href", "");
            link.setAttribute("target", "");
            preview.setAttribute("src", "");
            help.setAttribute("style", "display:none");
        }
    }
    else {
        background.style.backgroundImage = "url('" + ThumbURL +"')";
        background.style.border = 'none';
        background.innerHTML = '&nbsp;';
    }
    this.close();
}

