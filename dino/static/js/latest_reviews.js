// Example script to enhance interactivity, such as handling clicks on reviews
document.querySelectorAll('.review').forEach(review => {
  review.addEventListener('click', () => {
    alert('Review clicked!');
  });
});
