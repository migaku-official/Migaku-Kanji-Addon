function ReplaceTagsWithImages(src, img_uri=primitives_uri) {
    if (src.includes('[')) {
        // replace [tag] with image link to tag.svg, but skip strike counts (such as [3])
        const reg =  /\[([a-zA-Z\-_]+)\]/g
        return src.replace(reg, '<' + 'img src="' + img_uri + '$1.svg">');
    }
    return src;
}

function display_characters(page_type) {

    if (data.character[0] == '[') {
        let img = ReplaceTagsWithImages(data.character)
        let img_cursive = ReplaceTagsWithImages(data.character, cursive_primitives_uri)
        $('#character_img_1').html(img);
        $('#character_img_2').html(img_cursive);
        $('#character_img_3').html('');
        $('#character_img_4').html('');
    } else {
        if (page_type == "recognition") {
            $('.keyword-kanji').html(data.character);
        } else {
            $('.fontExample').html(data.character);    
        }
    }
}
