<script lang="ts">
    let files = $state<File[]>([]);

    function handleFilesChange(event: Event) {
        const input = event.target as HTMLInputElement;
        // Input checking
        if (!input) {
            console.error('Null files event');
            return;
        }

        const inputFiles = input.files;
        if (!inputFiles || inputFiles.length === 0) {
            console.warn('No files selected');
            return;
        }

        // Files are good, send over to server
        files = Array.from(inputFiles);
    }

    async function handleFilesSubmit() {
        // Input checking
        if (files.length == 0) {
            console.error('No files selected');
            return;
        }

        // Build form data to send to server
        let formData = new FormData();
        files.forEach((file) => formData.append('files', file));

        // Send, Process Files 
        if (!sendFiles(formData)) {
            return;
        } 
    }

    async function sendFiles(formData: FormData) {
        // Send to server
        const url = 'http://127.0.0.1:8000'
        const result = await fetch(url + "/upload_files/", {
            method: 'post',
            body: formData,
        });

        if (!result.ok) {
            console.error('Bad response to file upload');
            return false;
        }

        return true;
    }
</script>

<div class="flex h-[75vh] w-[75vw] flex-row text-left">
    <div class="m-5 flex h-full flex-1 flex-col rounded-xl bg-slate-600/30 p-5">
        <div>
            <label for="notes">Choose your notes:</label>
            <div class="flex flex-column justify-between w-full">
                <input
                    multiple
                    onchange={handleFilesChange}
                    type="file"
                    id="notes"
                    name="notes"
                    accept="image/*"
                    class="mt-1 block cursor-pointer rounded-lg border-white bg-gray-600 p-1 align-middle"
                />
                <button 
                    type="button" onclick={handleFilesSubmit}
                    class="mt-1 block border-white bg-gray-600 hover:bp-gray-800 p-1 rounded-lg align-middle text-center hover:cursor-pointer"
                > Convert! </button>
            </div>
        </div>
        <div class="flex-1 overflow-auto">
            <ul class="list-inside list-disc">
                {#each files as file}
                    <li>{file.name}</li>
                {/each}
            </ul>
        </div>
    </div>
    <div class="m-5 h-full flex-1 rounded-xl bg-slate-600/30 p-5">
        <h2>This is content as well!</h2>
    </div>
</div>
