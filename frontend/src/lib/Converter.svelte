<script lang="ts">
    let files = $state<File[]>([]);
    let markdowns = $state<String[]>([]);

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

    async function handleFilesSubmit() { // Hanlde file not existing?
        // Input checking
        if (files.length == 0) {
            console.error('No files selected');
            return;
        }

        // Clear markdowns
        markdowns = [];

        // Process each file individually
        for (const file of files) {
            // Create form to send file
            const formData = new FormData();
            formData.append('file', file);

            // Process file, result should contain md
            const md = await processFile(formData);
            if (md) {
                markdowns.push(md);
            } else {
                markdowns.push('Error occurred while processing');
            }
        }
    }

    async function processFile(formData: FormData) {
        // Send to server
        const url = 'http://127.0.0.1:8000';
        const result = await fetch(url + '/process_file/', {
            method: 'post',
            body: formData,
        });

        // Check for any issues
        if (!result.ok) {
            console.error('Bad response to file upload');
            return null;
        }

        // Parse result
        const data = await result.json();
        const md = data.markdown;

        return md;
    }
</script>

<div class="flex h-[75vh] w-[75vw] flex-row flex-wrap text-left">
    <div class="min-w-[400px] m-5 flex h-full flex-1 flex-col rounded-xl bg-slate-600/30 p-5">
        <div>
            <label for="notes">Choose your notes:</label>
            <div class="flex-column flex w-full justify-between">
                <input
                    multiple
                    onchange={handleFilesChange}
                    type="file"
                    id="notes"
                    name="notes"
                    accept="image/*"
                    class="mt-1 mr-5 block cursor-pointer rounded-lg border-white bg-gray-600 p-1 align-middle"
                />
                <button
                    type="button"
                    onclick={handleFilesSubmit}
                    class="mt-1 block rounded-lg border-white bg-gray-600 p-1 text-center align-middle hover:cursor-pointer hover:bg-gray-700"
                >
                    Convert!
                </button>
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
    <div class="min-w-[400px] m-5 flex h-full flex-1 flex-col rounded-xl bg-slate-600/30 p-5">
        <h2>Here are your results:</h2>
        <div class="flex-1 overflow-auto">
            <ul class="list-inside list-none">
                {#each markdowns as md}
                    <li class="mt-1 rounded bg-gray-600 p-1">{md}</li>
                {/each}
            </ul>
        </div>
    </div>
</div>
