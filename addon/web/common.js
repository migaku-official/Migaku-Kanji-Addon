function ReplaceTagsWithImages(src) {
    if (src.includes('[')) {
        // replace [tag] with image link to tag.svg, but skip strike counts (such as [3])
        const reg =  /\[([a-zA-Z\-_]+)\]/g
        return src.replace(reg, '<' + 'img src="' + primitives_uri + '$1.svg">');
    }
    return src;
}
