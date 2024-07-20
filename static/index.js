let currentMediaIndex = -1;
let currentMediaArray = [];

async function readRoute(route) {
    try {
        const response = await fetch(route);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error(`Failed to fetch data from ${route}:`, error);
        return null;
    }
}

/*
async function generateVideoThumbnail(file) {
    return new Promise((resolve, reject) => {
        const video = document.createElement('video');
        video.src = URL.createObjectURL(file);
        
        video.addEventListener('loadedmetadata', () => {
            video.currentTime = 5;
        });

        video.addEventListener('seeked', () => {
            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;

            const ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

            const thumbnail = canvas.toDataURL('image/jpeg');
            URL.revokeObjectURL(video.src);
            resolve(thumbnail);
        });

        video.addEventListener('error', (e) => {
            reject(e);
        });

        video.addEventListener('seeked', () => {
            video.pause();
        });
    });
}

async function getThumbnail(path) {
    const extension = path.split('.').pop().toLowerCase();
    if (['mp4', 'webm', 'ogg'].includes(extension)) {
        try {
            const response = await fetch(`/media${path}`);
            const blob = await response.blob();
            const thumbnail = await generateVideoThumbnail(blob);
            return thumbnail;
        } catch (error) {
            console.error('Failed to generate video thumbnail:', error);
            return '/path/to/default/thumbnail.jpg';
        }
    } else {
        return `/media${path}`;
    }
}
*/

async function getThumbnail(path, type) {
    const extension = path.split('.').pop().toLowerCase();
    if (type === 'video') {
        return `/thumbnail${path}`;
    } else {
        return `/media${path}`;
    }
}

async function displayData(route) {
    const data = await readRoute(route);
    if (data === null) {
        const container = document.getElementById('dataContainer');
        if (container) {
            container.textContent = 'Failed to fetch data.';
        }
        return;
    }

    const container = document.getElementById('dataContainer');
    if (container) {
        container.innerHTML = '';

        for (const [groupName, paths, types] of data) {
            // Assuming paths and types are comma-separated strings
            const pathsArray = paths.split(',').map(s => s.trim());
            const typesArray = types.split(',').map(s => s.trim());

            // Generate thumbnails for each file based on its type
            const thumbnailsPromises = pathsArray.map(async (path, index) => {
                const fileType = typesArray[index];
                const thumbnailPath = await getThumbnail(path, fileType); 
                return thumbnailPath;
            });

            const thumbnails = await Promise.all(thumbnailsPromises);

            // Create group card
            const groupCard = document.createElement('div');
            groupCard.className = 'card group';
            groupCard.innerHTML = `
                <img src="${thumbnails[0]}" alt="${groupName}" class="thumbnail"> <!-- Using the first thumbnail -->
                <div class="group-name">${groupName}</div>
            `;
            groupCard.addEventListener('click', () => displayGroup(groupName, pathsArray, typesArray));
            container.appendChild(groupCard);
        }
    } else {
        console.error('Container element not found');
    }
}

async function displayGroup(groupName, pathsArray, typesArray) {
    const container = document.getElementById('dataContainer');
    if (container) {
        container.innerHTML = '';

        for (let i = 0; i < pathsArray.length; i++) {
            const path = pathsArray[i].trim();
            const fileType = typesArray[i];
            const thumbnail = await getThumbnail(path, fileType); 
            const mediaCard = document.createElement('div');
            mediaCard.className = 'card';
            mediaCard.innerHTML = `
                <img src="${thumbnail}" alt="${groupName}" class="thumbnail">
            `;
            mediaCard.addEventListener('click', () => openMedia(pathsArray, i, typesArray));
            container.appendChild(mediaCard);
        }
    } else {
        console.error('Container element not found');
    }
}

function openMedia(mediaArray, mediaIndex, typesArray) {
    currentMediaArray = mediaArray;
    currentMediaIndex = mediaIndex;

    const mediaUrl = `/media${currentMediaArray[currentMediaIndex]}`;
    const mediaType = typesArray[currentMediaIndex]; // Get the file type directly
    const mediaContent = document.getElementById('mediaContent');
    const floatingWindow = document.getElementById('floatingWindow');

    if (mediaType === 'vid') { // Check if the file is a video
        mediaContent.innerHTML = `<video src="${mediaUrl}" controls autoplay style="max-width: 100%; max-height: 100%;"></video>`;
    } else {
        mediaContent.innerHTML = `<img src="${mediaUrl}" alt="Media" style="max-width: 100%; max-height: 100%;">`;
    }

    floatingWindow.style.display = 'block';
}

function closeMedia() {
    const floatingWindow = document.getElementById('floatingWindow');
    floatingWindow.style.display = 'none';
    document.getElementById('mediaContent').innerHTML = '';
}

function prevMedia() {
    if (currentMediaIndex > 0) {
        openMedia(currentMediaArray, currentMediaIndex - 1, currentMediaArray[currentMediaIndex - 1]);
    }
}

function nextMedia() {
    if (currentMediaIndex < currentMediaArray.length - 1) {
        openMedia(currentMediaArray, currentMediaIndex + 1, currentMediaArray[currentMediaIndex + 1]);
    }
}
