let imageSrc = null
let cible = document.getElementById('preview')
let previewValue = cible && cible.getAttribute('src')
const showPreview = (e) => {
  if (e.target.files && e.target.files[0]) {
    imageFile = e.target.files[0]
    const reader = new FileReader()
    reader.onload = (x) => {
      imageSrc = x.target.result
      cible.setAttribute('src', imageSrc)
    }
    reader.readAsDataURL(imageFile)
  } else {
    cible.setAttribute('src', previewValue)
  }
}
