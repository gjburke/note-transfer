<script lang="ts">
    let files = $state<File[]>([]);

    function handleFilesChange(event: Event) {
        const input = event.target as HTMLInputElement;
        if (!input) {
            console.error('Null files event');
            return;
        }

        const input_files = input.files;
        if (!input_files || input_files.length === 0) {
            console.warn('No files selected');
            return;
        }

        files = Array.from(input_files);
        console.log(files);
    }
</script>

<div class="flex h-[75vh] w-[75vw] flex-row text-left">
    <div class="m-5 flex h-full flex-1 flex-col rounded-xl bg-slate-600/30 p-5">
        <div>
            <label for="notes">Choose your notes:</label>
            <input
                multiple
                onchange={handleFilesChange}
                type="file"
                id="notes"
                name="notes"
                accept="image/*"
                class="mt-1 block cursor-pointer rounded-lg border-white bg-gray-600 p-1 align-middle"
            />
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
