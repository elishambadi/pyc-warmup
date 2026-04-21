'{{ widget.name }}-youtube': {
    command: (editor) => {
        const url = window.prompt('Paste a YouTube URL')
        if (!url) return

        editor
            .chain()
            .focus()
            .setYoutubeVideo({
                src: url,
                width: 640,
                height: 360,
            })
            .run()
    },
    canBeActive: false,
    tooltip: 'Insert YouTube video',
}