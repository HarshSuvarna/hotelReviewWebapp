document.addEventListener('DOMContentLoaded', function() {
    let currentIndex = 0;
    const items = document.querySelectorAll('.carousel-item');
    const totalItems = items.length;
    const switchTime = 3000; // 自动切换时间间隔，单位为毫秒
    
    function updateCarousel(newIndex) {
      currentIndex = newIndex;
      const translateX = -currentIndex * 100; // 计算需要移动的距离
      document.querySelector('.carousel-items').style.transform = `translateX(${translateX}%)`;
    }
  
    // 自动播放逻辑
    function autoPlay() {
      const newIndex = (currentIndex + 1) % totalItems;
      updateCarousel(newIndex);
    }
    let autoPlayInterval = setInterval(autoPlay, switchTime);
  
    // 重置自动播放定时器
    function resetAutoPlay() {
      clearInterval(autoPlayInterval);
      autoPlayInterval = setInterval(autoPlay, switchTime);
    }
  
    // 手动切换至上一个项
    document.querySelector('.prev').addEventListener('click', function(e) {
      e.preventDefault();
      const newIndex = (currentIndex - 1 + totalItems) % totalItems;
      updateCarousel(newIndex);
      resetAutoPlay();
    });
  
    // 手动切换至下一个项
    document.querySelector('.next').addEventListener('click', function(e) {
      e.preventDefault();
      const newIndex = (currentIndex + 1) % totalItems;
      updateCarousel(newIndex);
      resetAutoPlay();
    });
  });
  