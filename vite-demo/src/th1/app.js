function app() {
    return {
        data: [],
        show: false,
        toggleShow(id) {
            this.data[id].details = !this.data[id].details;
        }
    }
}