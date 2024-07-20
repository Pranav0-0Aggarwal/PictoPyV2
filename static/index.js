// Fetch data from a route
async function readRoute(route) {
    try {
        const response = await fetch(route);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`Failed to fetch data from ${route}:`, error);
        return null;
    }
}

// Get thumbnail URL based on the media type
async function getThumbnail(path, type) {
    if (type === 'vid') {
        return `/thumbnail${path}`;
    } else {
        return `/media${path}`;
    }
}

// Fetch thumbnails for a list of paths and types
async function fetchThumbnails(paths, types) {
    const thumbnailsPromises = paths.map(async (path, index) => {
        const fileType = types[index];
        return getThumbnail(path, fileType); 
    });

    return await Promise.all(thumbnailsPromises);
}

// Create a card element
function createCard(type, thumbnailSrc, altText, name = '') {
    const card = document.createElement('div');
    card.className = 'card';

    if (type === 'group') {
        card.classList.add('group');
        card.innerHTML = `
            <img src="${thumbnailSrc}" alt="${altText}" class="thumbnail">
            <div class="group-name">${name}</div>
        `;
    } else {
        card.innerHTML = `
            <img src="${thumbnailSrc}" alt="${altText}" class="thumbnail">
        `;
    }

    return card;
}

// Display group cards with data
async function displayData(route) {
    const data = await readRoute(route);
    const container = document.getElementById('dataContainer');
    
    if (!data || !container) {
        if (container) container.textContent = 'Failed to fetch data.';
        return;
    }

    container.innerHTML = '';

    for (const [groupName, paths, types] of data) {
        const pathsArray = paths.split(',').map(s => s.trim());
        const typesArray = types.split(',').map(s => s.trim());

        const thumbnails = await fetchThumbnails(pathsArray, typesArray);

        const groupCard = createCard('group', thumbnails[0], groupName, groupName);
        groupCard.addEventListener('click', () => displayGroup(groupName, pathsArray, typesArray));
        container.appendChild(groupCard);
    }
}

// Display media cards within a group
async function displayGroup(groupName, pathsArray, typesArray) {
    const container = document.getElementById('dataContainer');
    
    if (!container) {
        console.error('Container element not found');
        return;
    }

    container.innerHTML = '';

    for (let i = 0; i < pathsArray.length; i++) {
        const path = pathsArray[i].trim();
        const fileType = typesArray[i];
        const thumbnail = await getThumbnail(path, fileType); 

        const mediaCard = createCard('media', thumbnail, groupName);
        mediaCard.addEventListener('click', () => openMedia(pathsArray, i, typesArray));
        container.appendChild(mediaCard);
    }
}

// Open a media file in a floating window
function openMedia(mediaArray, mediaIndex, typesArray) {
    currentMediaArray = mediaArray;
    currentMediaIndex = mediaIndex;
    currentMediaTypesArray = typesArray; 

    const mediaUrl = `/media${currentMediaArray[currentMediaIndex]}`;
    const mediaType = currentMediaTypesArray[currentMediaIndex]; 
    const mediaContent = document.getElementById('mediaContent');
    const floatingWindow = document.getElementById('floatingWindow');

    if (mediaType === 'vid') {
        mediaContent.innerHTML = `<video src="${mediaUrl}" controls autoplay style="max-width: 100%; max-height: 100%;"></video>`;
    } else {
        mediaContent.innerHTML = `<img src="${mediaUrl}" alt="Media" style="max-width: 100%; max-height: 100%;">`;
    }

    floatingWindow.style.display = 'block';
}

// Close the floating media window
function closeMedia() {
    const floatingWindow = document.getElementById('floatingWindow');
    floatingWindow.style.display = 'none';
    document.getElementById('mediaContent').innerHTML = '';
}

// Navigate to the previous media item
function prevMedia() {
    if (currentMediaIndex > 0) {
        openMedia(currentMediaArray, currentMediaIndex - 1, currentMediaTypesArray);
    }
}

// Navigate to the next media item
function nextMedia() {
    if (currentMediaIndex < currentMediaArray.length - 1) {
        openMedia(currentMediaArray, currentMediaIndex + 1, currentMediaTypesArray);
    }
}

// Toggle grouping of media by directory or class
function toggleGroup() {
    groupBy = groupBy === "directory" ? "class" : "directory";
    displayData(`/${section}${groupBy}`);
}

// Toggle between displaying images and videos
function toggleSection() {
    section = section === "img" ? "vid" : "img";
    displayData(`/${section}${groupBy}`);
}

// Display images based on the current section and grouping
function displayImages() {
    displayData("/img/directory");
}

// Display videos based on the current section and grouping
function displayVideos() {
    displayData("/vid/directory");
}

// Initialize variables
let currentMediaIndex = -1;
let currentMediaArray = [];
let currentMediaTypesArray = []; 
let section = "img/";
let groupBy = "directory";

// Initial data display
displayData(`/${section}${groupBy}`);
