# Pacific Economy Data Visualization Dashboard 🌊

An interactive web application for visualizing economic and social indicators across Pacific Island Countries and territories, aligned with Sustainable Development Goal 8 (Decent Work and Economic Growth).

**Team Members:**
- Rizal Wahyu Pratama (2311110029)
- Khulika Malkan (2311110057)  
- Mikhael Setia Budi (2311110033)

## ✨ Features

### 🎨 Modern UI/UX
- **Gradient backgrounds** with glassmorphism effects
- **Interactive tabs** with smooth transitions
- **Responsive design** that works on all devices
- **Professional typography** using Inter font family
- **Enhanced color scheme** with CSS custom properties
- **Loading states** and animations for better user feedback

### 📊 Advanced Visualizations
- **Statistical Analysis**: Enhanced bar charts with color mapping and hover tooltips
- **Geographic Distribution**: Improved box plots showing statistical summaries
- **Temporal Trends**: Interactive line charts with country-specific data
- **Dynamic legends** and interactive elements
- **Color-coded categories** for better visual distinction

### 🚀 Enhanced Functionality
- **Real-time form validation** with user-friendly error messages
- **Auto-save selections** using localStorage
- **Keyboard navigation** (Ctrl+1,2,3 for tab switching)
- **Flash messaging system** for user notifications
- **Error handling** with graceful fallbacks
- **API endpoints** for dynamic data loading

### 🔧 Technical Improvements
- **Modular JavaScript architecture** with ES6 classes
- **Enhanced Flask backend** with logging and error handling
- **Better data processing** with statistical calculations
- **Improved security** with input validation
- **Production-ready** with gunicorn support

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation Steps

1. **Clone or navigate to the project directory**
   ```bash
   cd dataviz-competition
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify data file exists**
   Ensure the CSV file is in the correct location:
   ```
   data/Sustainable Development Goal 08 - Decent Work and Economic Growth data.csv
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   Open your browser and navigate to: `http://localhost:5000`

## 📁 Project Structure

```
dataviz-competition/
├── app.py                     # Enhanced Flask application
├── requirements.txt           # Updated dependencies
├── README.md                 # This file
├── data/
│   └── Sustainable Development Goal 08 - Decent Work and Economic Growth data.csv
├── static/
│   ├── css/
│   │   └── style.css         # Modern CSS with custom properties
│   ├── js/
│   │   └── app.js           # Enhanced JavaScript functionality
│   └── images/
│       └── Pasific Map.png
└── templates/
    ├── index.html            # Redesigned main template
    └── layout.html           # Base layout (future use)
```

## 🎯 Data Categories

The dashboard organizes SDG 8 indicators into four main categories:

### 💰 Economic Development
- Average hourly earnings
- Aid for Trade flows
- Financial inclusion metrics

### 👥 Employment & Labor  
- GDP per employed person
- Unemployment rates
- Youth employment statistics

### 🏝️ Trade & Tourism
- Child labor indicators
- Tourism GDP contribution
- Economic diversification metrics

### 🌱 Social Development
- Sustainable growth indicators
- Regional development patterns

## 🎨 UI/UX Enhancements

### Visual Design
- **Color Palette**: Professional blue-green gradient theme
- **Typography**: Inter font family for modern readability
- **Spacing**: Consistent spacing using CSS custom properties
- **Icons**: Lucide icons for better visual communication

### Interactive Elements
- **Hover Effects**: Subtle animations on buttons and cards
- **Form Validation**: Real-time feedback with error highlighting
- **Loading States**: Progress indicators during data processing
- **Toast Notifications**: Non-intrusive success/error messages

### Accessibility
- **Keyboard Navigation**: Full keyboard support
- **Screen Reader Friendly**: Proper ARIA labels and semantic HTML
- **High Contrast**: Accessible color combinations
- **Focus Indicators**: Clear focus states for all interactive elements

## 🔧 Technical Features

### Frontend Enhancements
- **Modular JavaScript**: Object-oriented approach with ES6 classes
- **Local Storage**: Persistent user preferences
- **Error Handling**: Graceful degradation and error recovery
- **Performance**: Optimized animations and transitions

### Backend Improvements
- **Enhanced Error Handling**: Comprehensive try-catch blocks
- **Logging**: Structured logging for debugging
- **Input Validation**: Server-side validation for security
- **API Endpoints**: RESTful endpoints for dynamic data

### Data Processing
- **Statistical Analysis**: Enhanced box plot calculations
- **Data Cleaning**: Robust data preprocessing
- **Aggregation**: Smart data aggregation for visualizations
- **Error Recovery**: Fallback mechanisms for missing data

## 🚀 Deployment

### Development
```bash
python app.py
```

### Production (with Gunicorn)
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Environment Variables
- `PORT`: Application port (default: 5000)
- `FLASK_DEBUG`: Debug mode (default: True)

## 🐛 Troubleshooting

### Common Issues

1. **CSV File Not Found**
   - Ensure the CSV file is in the `data/` directory
   - Check file name matches exactly

2. **Dependencies Missing**
   - Run `pip install -r requirements.txt`
   - Use virtual environment if needed

3. **Port Already in Use**
   - Change the port in `app.py` or set `PORT` environment variable

4. **Visualizations Not Loading**
   - Check browser console for JavaScript errors
   - Ensure Bokeh CDN is accessible

## 🔮 Future Enhancements

- [ ] Dark mode toggle
- [ ] Data export functionality
- [ ] Advanced filtering options
- [ ] User authentication
- [ ] Dashboard customization
- [ ] Real-time data updates
- [ ] Mobile app version
- [ ] Multi-language support

## 📄 License

This project is part of a data visualization competition focused on Pacific Island economic development and SDG 8 indicators.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

**Built with ❤️ for Pacific Island economic development visualization**
