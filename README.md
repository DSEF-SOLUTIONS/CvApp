# End of study Project : CV App

“CV App”, an exceptional achievement designed to simplify the process of pre-selection of profiles within companies. This end-of-study project is based on a comprehensive machine learning approach, offering an innovative Flask application for precise predictions on applications. Thanks to "CV App", optimize your selection process and gain efficiency. Choose excellence with this one-of-a-kind project.

## Authors

- [@kaoutharmsafri](https://github.com/kaoutharmsafri)

## Color Reference

| Color             | Hex                                                                |
| ----------------- | ------------------------------------------------------------------ |
| Orange  | ![#fb4c1c](https://via.placeholder.com/10/fb4c1c?text=+) #fb4c1c |
| Grey | ![#383535](https://via.placeholder.com/10/383535?text=+) #383535 |
| Black | ![#141414](https://via.placeholder.com/10/141414?text=+) #141414 |
| Light orange | ![#ed6d1e](https://via.placeholder.com/10/ed6d1e?text=+) #ed6d1e |
| Yellow | ![#fea223](https://via.placeholder.com/10/fea223?text=+) #fea223 |



![Logo](https://github.com/kaoutharmsafri/cvapp/blob/main/static/images/iphone-screen.png)


## Roadmap
**Data Lifecycle:**

- **Data Collection**: Web scraping and the LinkedIn API were utilized for data collection.

- **Data Labeling**: Collaboration with the HR department resulted in data labeling for algorithm training. A coherent and effective data labeling method using weighted equations was developed, which was approved by our supervising professor.

- **Data Cleaning and Preprocessing**: MinMaxScaler was applied for normalization, and weights for experience and skill level were set. Data cleaning techniques, including encoding categorical columns, handling outliers, and removing redundant columns and spelling errors, were implemented.

- **Data Modeling**: Various classification models, including logistic regression, linear discriminant analysis, naive Bayes, k-nearest neighbors, support vector machine, and decision tree, were trained. Hyperparameter optimization using GridSearchCV was conducted, resulting in promising results. Ensemble learning techniques such as XGBoost, gradient boosting, stacking classifier, and bagging were explored.

- **Data Testing**: Model performance on new data was evaluated, achieving high accuracy. A Streamlit application was developed for user-friendly interaction and visualization.


**Web Application Development:**

- **Application Development with Flask**:The application was created with various pages such as home, database, and visitor messages. Each page was meticulously designed to serve specific functionalities and ensure a seamless user experience. CSS and Bootstrap were integrated to enhance the application's visual appeal, aiming for a modern and user-friendly interface. MySQL was chosen for efficient database management, with XAMPP and phpMyAdmin facilitating seamless access and administration, simplifying tasks such as data manipulation and retrieval.

- **Database Deployment on Azure SQL Database**:Transitioning the database to Azure SQL Database allowed for leveraging the scalability and accessibility of cloud platforms. This migration ensured improved reliability, availability, and simplified data management and administration. Hosting the database on Azure facilitated easier access and collaboration on data-related tasks, enhancing overall application efficiency.

- **Creation of Azure Container**:Following containerization best practices, an Azure container was created to encapsulate and isolate application components. Containers provide a lightweight, portable environment for deploying and running applications, ensuring consistency across different environments. This approach streamlined deployment processes and minimized dependencies, enhancing portability and ease of management.

- **Building Image in Azure Container**:Compiling all necessary dependencies and configurations into a single package prepared the application for deployment. Encapsulating the application within an image ensured consistent deployment across different environments, eliminating potential compatibility issues and ensuring seamless deployment.

- **Configuration of Azure Web App**:Leveraging Azure services, an Azure web app was created and meticulously configured to utilize the image from the Azure container. This setup enabled efficient deployment and optimized performance of the web application on the Azure platform. Configuring the web app to use the containerized image facilitated rapid deployment and scaling in line with changing demands and requirements.

- **Automation with GitHub Actions**:Configuring GitHub Actions streamlined the deployment process, ensuring continuous integration and delivery. Automation of routine tasks such as testing, building, and deploying the application enhanced productivity and maintained code consistency. GitHub Actions provided a powerful workflow automation tool, seamlessly integrating with Azure services and facilitating efficient collaboration among team members.

This roadmap outlines the key steps taken in our project, from data collection to the development and deployment of our web application. Each phase has been meticulously executed to ensure the success of our project.